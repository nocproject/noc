#!./bin/python
# ---------------------------------------------------------------------
# Basic MO discovery job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import contextlib
import zlib
import datetime
import types
import operator
from io import StringIO
from time import perf_counter

# Third-party modules
import bson
import cachetools
import orjson
from pymongo import UpdateOne
from typing import List, Dict, Any, Optional, Tuple
from builtins import str, object

# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.core.models.problem import ProblemItem
from noc.main.models.label import Label, MATCH_OPS
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.debug import error_report
from noc.core.log import PrefixLoggerAdapter
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.mongo.connection import get_db
from noc.core.service.error import RPCError, RPCRemoteError
from noc.core.error import (
    ERR_CLI_AUTH_FAILED,
    ERR_CLI_NO_SUPER_COMMAND,
    ERR_CLI_LOW_PRIVILEGES,
    ERR_CLI_SSH_PROTOCOL_ERROR,
    ERR_CLI_CONNECTION_REFUSED,
    ERR_CLI_PASSWORD_TIMEOUT,
)
from noc.core.span import Span
from noc.core.cache.base import cache
from noc.core.perf import metrics
from noc.core.comp import smart_bytes
from noc.core.wf.interaction import Interaction
from noc.core.wf.diagnostic import DiagnosticState, DiagnosticHub


class MODiscoveryJob(PeriodicJob):
    model = ManagedObject
    use_get_by_id = True
    use_offset = True
    # Name of umbrella class to cover discovery problems
    umbrella_cls = None
    # Job families
    is_box = False
    is_periodic = False
    # Get diagnostics with enabled discovery (Box/Periodic filtered)
    discovery_diagnostics = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.out_buffer = StringIO()
        self.logger = PrefixLoggerAdapter(self.logger, "", target=self.out_buffer)
        self.check_timings = []
        self.problems: List[ProblemItem] = []
        self.caps = None
        self.has_fatal_error = False
        self.service = self.scheduler.service
        # Additional artefacts can be passed between checks in one session
        self.artefacts = {}

    def schedule_next(self, status):
        if self.check_timings:
            self.logger.info(
                "Timings: %s",
                ", ".join("%s = %.2fms" % (n, t * 1000) for n, t in self.check_timings),
            )
        super().schedule_next(status)
        # Update alarm statuses
        # Clean up all open alarms as they has been disabled
        if self.get_umbrella_settings():
            self.update_alarms(self.problems, self.umbrella_cls)
        # Update diagnostics statuses
        self.update_diagnostics(self.problems)
        # Write job log
        key = "discovery-%s-%s" % (self.attrs[self.ATTR_CLASS], self.attrs[self.ATTR_KEY])
        problems = {}
        for p in list(self.problems):
            if not p.check:
                # Not Discovery problem
                continue
            path = " | ".join(p.path)
            if p.check not in problems:
                problems[p.check] = defaultdict(str)
            if p.path:
                problems[p.check][path] = p.message
            else:
                # p["path"] == ""
                problems[p.check][path] += f"; {p.message}"

        get_db()["noc.joblog"].update_one(
            {"_id": key},
            {
                "$set": {
                    "log": bson.Binary(zlib.compress(smart_bytes(self.out_buffer.getvalue()))),
                    "problems": problems,
                }
            },
            upsert=True,
        )

    def get_running_policy(self):
        raise NotImplementedError

    def can_run(self):
        # Check object is managed
        if (
            Interaction.BoxDiscovery not in self.object.interactions
            and Interaction.PeriodicDiscovery not in self.object.interactions
        ):
            self.logger.info("Run Discovery on Object is not allowed. Skipping job")
            return False
        return True

    @contextlib.contextmanager
    def check_timer(self, name):
        t = perf_counter()
        yield
        self.check_timings += [(name, perf_counter() - t)]

    def set_problem(
        self,
        check: Optional[str] = None,
        alarm_class: Optional[str] = None,
        path: Optional[List[str]] = None,
        message: Optional[str] = None,
        fatal: bool = False,
        diagnostic: Optional[str] = None,
        **kwargs,
    ):
        """
        Set discovery problem
        :param check: Check name
        :param alarm_class: Alarm class instance or name
        :param path: Additional path
        :param message: Text message
        :param fatal: True if problem is fatal and all following checks
            must be disabled
        :param diagnostic: Diagnostic name affected by problem
        :param kwargs: Optional variables
        :return:
        """
        self.logger.debug(
            "[%s] Set problem: class=%s diagnostic=%s path=%s message=%s fatal=%s vars=%s",
            check,
            alarm_class,
            diagnostic,
            path,
            message,
            fatal,
            kwargs,
        )
        self.problems += [
            ProblemItem(
                **{
                    "check": check,
                    "alarm_class": alarm_class,
                    # in MongoDB Key must be string
                    # "path": [str(path)] if path else [],
                    "labels": [],
                    "diagnostic": diagnostic,
                    "message": message,
                    "fatal": fatal,
                    "vars": kwargs,
                }
            )
        ]
        if fatal:
            self.has_fatal_error = True

    def set_fatal_error(self):
        self.has_fatal_error = True

    def get_caps(self):
        """
        Return object's capabilities
        :return:
        """
        if self.caps is None:
            self.caps = self.object.get_caps()
        return self.caps

    def update_caps(self, caps, source):
        self.caps = self.object.update_caps(caps, source=source)

    def allow_sessions(self):
        r = self.object.can_cli_session()
        if r:
            self.object.get_profile().allow_cli_session(None, None)
        return r

    def load_diagnostic(self, is_box: bool = False, is_periodic: bool = False):
        r = set()
        for dc in self.object.iter_diagnostic_configs():
            if (is_box and not dc.discovery_box) or (is_periodic and not dc.discovery_periodic):
                continue
            # if dc.run_order != self.run_order:
            #     continue
            if not dc.checks or dc.blocked:
                # Diagnostic without checks
                continue
            if dc.run_policy not in {"A", "F"}:
                continue
            r.add(dc.diagnostic)
        return r

    def update_diagnostics(self, problems: List[ProblemItem]):
        """
        Syn problems to object diagnostic statuses
        :param problems:
        :return:
        """
        #
        discovery_diagnostics = self.load_diagnostic(
            is_box=self.is_box, is_periodic=self.is_periodic
        )
        self.logger.debug("Updating diagnostics statuses: %s", problems)
        if not discovery_diagnostics:
            self.logger.info("Discovered diagnostics not found")
            return None
        now = datetime.datetime.now()
        processed = set()
        # Processed failed diagnostics
        with DiagnosticHub(self.object, sync_alarm=self.can_update_alarms()) as d:
            for p in problems:
                if p.diagnostic and p.diagnostic in discovery_diagnostics:
                    d.set_state(
                        p.diagnostic,
                        state=DiagnosticState.failed,
                        reason=p.message,
                        changed_ts=now,
                    )
                    processed.add(p.diagnostic)
        # Set OK state
        # for diagnostic in discovery_diagnostics - processed:
        #     self.object.set_diagnostic_state(diagnostic, state=True, changed_ts=now, bulk=bulk)
        # if bulk:
        #     self.logger.info("Diagnostic changed: %s", ", ".join(di.diagnostic for di in bulk))
        #     self.object.save_diagnostics(self.object.id, bulk)
        #     if self.can_update_alarms():
        #         self.object.sync_diagnostic_alarm([d.diagnostic for d in bulk])

    def update_alarms(
        self, problems: List[ProblemItem], group_cls: str = None, group_reference: str = None
    ):
        """
        Sync problems to alarm and use active_problems context variable
        for check active alarm group.

        * If empty problems and `group reference` not in active_problems- do nothing
        * If empty problems and `group reference` in active_problems - send empty ensure_group to dispose and remove it from context
        * If has problems - send ensure_group to dispose and save reference_group to active_problems context

        :param problems: List problems
        :param group_cls: Group Alarm Class
        :param group_reference: Group Reference
        :return:
        """
        from noc.fm.models.alarmclass import AlarmClass

        self.logger.info("Updating alarm statuses")
        group_cls: Optional["AlarmClass"] = AlarmClass.get_by_name(group_cls or "Group")
        if not group_cls:
            self.logger.info("No umbrella alarm class. Alarm statuses not updated")
            return

        group_reference = group_reference or f"g:d:{self.object.id}:{group_cls.name}"
        active_problems: Dict[str, List[str]] = self.context.get("active_problems", {})
        if not problems and group_reference not in active_problems:
            # No money, no honey
            return
        details: List[Dict[str, Any]] = []
        now = datetime.datetime.now()
        for p in problems:
            if not p.alarm_class:
                continue
            ac = AlarmClass.get_by_name(p.alarm_class)
            if not ac:
                self.logger.info("Unknown alarm class %s. Skipping", p.alarm_class)
                continue
            d_vars = {"path": " | ".join(p.path), "message": p.message}
            if p.vars:
                d_vars.update(p.vars)
            labels = p.labels
            if p.fatal:
                labels += ["noc::is_fatal::="]
            details += [
                {
                    "reference": f"d:{p.alarm_class}:{self.object.id}:{' | '.join(p.path)}",
                    "alarm_class": p.alarm_class,
                    "managed_object": str(self.object.id),
                    "timestamp": now,
                    "labels": labels,
                    "vars": d_vars,
                }
            ]
        msg = {
            "$op": "ensure_group",
            "reference": group_reference,
            "alarm_class": group_cls.name,
            "alarms": details,
        }
        stream, partition = self.object.alarms_stream_and_partition
        self.service.publish(
            orjson.dumps(msg),
            stream=stream,
            partition=partition,
        )
        self.logger.debug(
            "Dispose: %s", orjson.dumps(msg, option=orjson.OPT_INDENT_2).decode("utf-8")
        )
        if not details and group_reference in active_problems:
            del active_problems[group_reference]
        else:
            active_problems[group_reference] = [d["reference"] for d in details]
        self.context["active_problems"] = active_problems

    def get_umbrella_settings(self) -> bool:
        """
        Check enable Alarm for Discovery
        :param self:
        :return:
        """
        prev_status = self.context.get("umbrella_settings", False)
        current_status = self.can_update_alarms()

        self.context["umbrella_settings"] = current_status

        if not prev_status and not current_status:
            return False
        return True

    def can_update_alarms(self):
        return False

    def get_fatal_alarm_weight(self):
        return 1

    def get_alarm_weight(self):
        return 1

    def set_artefact(self, name, value=None):
        """
        Set artefact (opaque structure to be passed to following checks)
        :param name: Artefact name
        :param value: Opaque value
        :return:
        """
        if not value:
            if name in self.artefacts:
                del self.artefacts[name]
        else:
            self.artefacts[name] = value or None

    def get_artefact(self, name):
        """
        Get artefact by name
        :param name: artefact name
        :return: artefact
        """
        return self.artefacts.get(name)

    def has_artefact(self, name):
        """
        Check job has existing artefact
        :param name: artefact name
        :return: True, if artefact exists, False otherwise
        """
        return name in self.artefacts


class DiscoveryCheck(object):
    name = None
    # If not none, check required script is available
    # before running check
    required_script = None
    # If not None, check object has all required capablities
    # from list
    required_capabilities = None
    # If not None, check job has all required artefacts
    required_artefacts = None
    #
    fatal_errors = {
        ERR_CLI_AUTH_FAILED,
        ERR_CLI_NO_SUPER_COMMAND,
        ERR_CLI_LOW_PRIVILEGES,
        ERR_CLI_CONNECTION_REFUSED,
        ERR_CLI_SSH_PROTOCOL_ERROR,
        ERR_CLI_PASSWORD_TIMEOUT,
    }
    # Error -> Alarm class mappings
    error_map = {
        ERR_CLI_AUTH_FAILED: "Discovery | Error | Auth Failed",
        ERR_CLI_PASSWORD_TIMEOUT: "Discovery | Error | Auth Failed",
        ERR_CLI_NO_SUPER_COMMAND: "Discovery | Error | No Super",
        ERR_CLI_LOW_PRIVILEGES: "Discovery | Error | Low Privileges",
        ERR_CLI_CONNECTION_REFUSED: "Discovery | Error | Connection Refused",
        ERR_CLI_SSH_PROTOCOL_ERROR: "Discovery | Error | SSH Protocol",
    }

    def __init__(self, job):
        self.service = job.service
        self.job = job
        self.object: ManagedObject = self.job.object
        self.logger = self.job.logger.get_logger("[%s" % self.name)
        self.if_name_cache = {}  # mo, name -> Interface
        self.if_mac_cache = {}  # mo, mac -> Interface
        self.if_ip_cache = {}
        self.sub_cache = {}
        self.profile_cache = {}
        self.is_box = self.job.is_box
        self.is_periodic = self.job.is_periodic

    def is_enabled(self):
        checks = self.job.attrs.get("_checks", set())
        return not checks or self.name in checks

    def has_fatal_error(self):
        return self.job.has_fatal_error

    def has_required_script(self):
        return not self.required_script or self.required_script in self.object.scripts

    def get_caps(self):
        return self.job.get_caps()

    def update_caps(self, caps, source):
        self.job.update_caps(caps, source)

    def has_capability(self, cap):
        return bool(self.get_caps().get(cap))

    def has_any_capability(self, caps):
        for c in caps:
            if self.has_capability(c):
                return True
        return False

    def has_required_capabilities(self):
        if not self.required_capabilities:
            return True
        caps = self.get_caps()
        for cn in self.required_capabilities:
            if cn not in caps:
                self.logger.info("Object hasn't required capability '%s'. " "Skipping", cn)
                return False
            v = caps[cn]
            if not v:
                self.logger.info("Capability '%s' is disabled. Skipping", cn)
                return False
        return True

    def has_required_artefacts(self):
        if not self.required_artefacts:
            return True
        for ra in self.required_artefacts:
            if not self.has_artefact(ra):
                self.logger.info("Job has not '%s' artefact. Skipping", ra)
                return False
        return True

    def run(self):
        if not self.is_enabled():
            self.logger.info("Check is disabled. Skipping")
            return
        if self.has_fatal_error():
            self.logger.info("Check is disabled due to previous fatal error. Skipping")
            return
        if not self.has_required_artefacts():
            return
        with Span(server="discovery", service=self.name) as span, self.job.check_timer(self.name):
            # Check required scripts
            if not self.has_required_script():
                self.logger.info("%s script is not supported. Skipping", self.required_script)
                return
            # Check required capabilities
            if not self.has_required_capabilities():
                return
            # Run check
            try:
                self.handler()
            except RPCRemoteError as e:
                self.logger.error("RPC Remote error (%s): %s", e.remote_code, e)
                if e.remote_code:
                    message = f"Remote error code {e.remote_code}"
                else:
                    message = f"Remote error code {e.remote_code}, message: {e}"
                self.set_problem(
                    message=message,
                    diagnostic="CLI" if e.remote_code in self.error_map else None,
                    fatal=e.remote_code in self.fatal_errors,
                )
                span.set_error_from_exc(e, e.remote_code)
            except RPCError as e:
                self.set_problem(
                    message=f"RPC Error: {e}",
                    diagnostic="CLI" if e.default_code in self.error_map else None,
                    fatal=e.default_code in self.fatal_errors,
                )
                self.logger.error("Terminated due RPC error: %s", e)
                span.set_error_from_exc(e, e.default_code)
            except Exception as e:
                self.set_problem(message=f"Unhandled exception: {e}")
                error_report(logger=self.logger)
                span.set_error_from_exc(e)

    def handler(self):
        pass

    @staticmethod
    def build_effective_labels(obj) -> List[str]:
        """
        Build object effective labels
        :param obj:
        :return:
        """
        return [
            ll
            for ll in sorted(Label.merge_labels(obj.iter_effective_labels(obj), add_wildcard=True))
            if obj.can_set_label(ll) or ll[-1] in MATCH_OPS or ll[-1] == "*"
        ]

    def update_if_changed(
        self,
        obj,
        values: Dict[str, Any],
        ignore_empty: List[str] = None,
        wait: bool = True,
        bulk: Optional[List[str]] = None,
        update_effective_labels: bool = False,
    ):
        """
        Update fields if changed.
        :param obj: Document instance
        :type obj: Document
        :param values: New values
        :type values: dict
        :param ignore_empty: List of fields which may be ignored if empty
        :param wait: Wait for operation to complete. set write concern to 0 if False
        :param bulk: Execute as the bulk op instead
        :param update_effective_labels:
        :returns: List of changed (key, value)
        :rtype: list
        """
        changes = []
        ignore_empty = ignore_empty or []
        for k, v in values.items():
            vv = getattr(obj, k)
            if hasattr(obj, "extra_labels") and k == "extra_labels":
                # Processed extra_labels
                sa_labels = obj.extra_labels.get("sa", [])
                if v != sa_labels:
                    remove_labels = set(sa_labels).difference(v)
                    if remove_labels:
                        obj.labels = [ll for ll in obj.labels if ll not in remove_labels]
                        changes += [("labels", obj.labels)]
                    obj.extra_labels.update({"sa": v})
                    changes += [("extra_labels", {"sa": v})]
                continue
            if v != vv:
                if not isinstance(v, int) or not hasattr(vv, "id") or v != vv.id:
                    if k in ignore_empty and (v is None or v == ""):
                        continue
                    setattr(obj, k, v)
                    changes += [(k, v)]
        if update_effective_labels and hasattr(obj, "effective_labels"):
            el = self.build_effective_labels(obj)
            if set(el) != set(getattr(obj, "effective_labels", [])):
                changes += [("effective_labels", el)]
        if changes:
            if bulk is not None:
                op = {"$set": dict(changes)}
                id_field = obj._fields[Interface._meta["id_field"]].db_field
                bulk += [UpdateOne({id_field: obj.pk}, op)]
            else:
                kwargs = {}
                if not wait:
                    kwargs["write_concern"] = {"w": 0}
                obj.save(**kwargs)
        return changes

    def log_changes(self, msg: str, changes: List[Tuple[str, Any]]):
        """
        Log changes
        :param msg: Message
        :type msg: str
        """
        if changes:
            self.logger.info("%s: %s" % (msg, ", ".join("%s = %s" % (k, v) for k, v in changes)))

    def get_interface_by_name(self, name, mo=None):
        """
        Returns Interface instance
        """
        mo = mo or self.object
        try:
            name = mo.get_profile().convert_interface_name(name)
        except ValueError as e:
            self.logger.debug("Cannot convert remote port %s:%r, %r", mo.name, name, e)
            return
        self.logger.debug("Searching port by name: %s:%s", mo.name, name)
        key = (mo, name)
        if key not in self.if_name_cache:
            i = Interface.objects.filter(managed_object=mo, name=name).first()
            self.if_name_cache[key] = i
        return self.if_name_cache[key]

    def get_interface_by_mac(self, mac, mo=None):
        """
        Returns Interface instance referred by MAC address
        """
        mo = mo or self.object
        self.logger.debug("Searching port by MAC: %s:%s", mo.name, mac)
        key = (mo, mac)
        if key not in self.if_mac_cache:
            i = Interface.objects.filter(managed_object=mo, mac=mac, type="physical")[:2]
            if len(i) == 1:
                i = i[0]
            else:
                i = None  # Non unique or not found
            self.if_mac_cache[key] = i
        return self.if_mac_cache[key]

    def get_interface_by_ip(self, ip, mo=None):
        """
        Returns Interface instance referred by IP address
        """
        mo = mo or self.object
        self.logger.debug("Searching port by IP: %s:%s", mo.name, ip)
        key = (mo, ip)
        if key not in self.if_ip_cache:
            li = list(
                Interface.objects.filter(
                    managed_object=self.object.id,
                    ipv4_addresses__startswith="%s/" % ip,
                    type="physical",
                )
            )
            if len(li) == 1:
                li = li[0]
            else:
                li = None  # Non unique or not found
            self.if_ip_cache[key] = li
        return self.if_ip_cache[key]

    def set_interface(self, name, iface):
        """
        Fill interface cache
        """
        key = (self.object, name)
        self.if_name_cache[key] = iface

    def get_subinterface(self, interface, name):
        """
        Returns Interface instance
        """
        key = (str(interface.id), name)
        if key not in self.sub_cache:
            si = SubInterface.objects.filter(interface=interface.id, name=name).first()
            self.sub_cache[key] = si
        return self.sub_cache[key]

    def get_interface_profile(self, name):
        if name not in self.profile_cache:
            p = InterfaceProfile.objects.filter(name=name).first()
            self.profile_cache[name] = p
        return self.profile_cache[name]

    def clear_links(self):
        """
        Clear all object's links
        """
        self.logger.info("Cleaning links")
        for i in Interface.objects.filter(
            managed_object=self.object.id, type__in=["physical", "aggregated", "virtual"]
        ):
            link = i.link
            if link:
                self.logger.info("Unlinking: %s", link)
                try:
                    i.unlink()
                except ValueError as e:
                    self.logger.info("Failed to unlink: %s", e)

    def set_problem(
        self,
        alarm_class: Optional[str] = None,
        path: Optional[List[str]] = None,
        message: Optional[str] = None,
        fatal: bool = False,
        diagnostic: Optional[str] = None,
        **kwargs,
    ):
        """
        Set discovery problem
        :param alarm_class: Alarm class instance or name
        :param path: Additional path
        :param message: Text message
        :param fatal: True if problem is fatal and all following checks
            must be disabled
        :param diagnostic: Diagnostic name affected by problem
        :param kwargs: Dict containing optional variables
        :return:
        """
        self.logger.info("Set path: %s", path)
        self.job.set_problem(
            check=self.name,
            alarm_class=alarm_class,
            path=path,
            diagnostic=diagnostic,
            message=message,
            fatal=fatal,
            **kwargs,
        )

    def set_artefact(self, name, value=None):
        """
        Set artefact (opaque structure to be passed to following checks)
        :param name: Artefact name
        :param value: Opaque value
        :return:
        """
        self.job.set_artefact(name, value)

    def get_artefact(self, name: str) -> Optional[Any]:
        """
        Get artefact by name
        :param name: artefact name
        :return: artefact
        """
        return self.job.get_artefact(name)

    def has_artefact(self, name):
        """
        Check job has existing artefact
        :param name: artefact name
        :return: True, if artefact exists, False otherwise
        """
        return self.job.has_artefact(name)

    def invalidate_neighbor_cache(self, obj=None):
        """
        Reset cached neighbors for object.

        NB: May be called by non-topology checks
        :param obj: Managed Object instance, jobs object if ommited
        :return:
        """
        obj = obj or self.object
        if not obj.object_profile.neighbor_cache_ttl:
            # Disabled cache
            return
        keys = [
            "mo-neighbors-%s-%s" % (x, obj.id) for x in obj.segment.profile.get_topology_methods()
        ]
        if keys:
            self.logger.info("Invalidating neighor cache: %s" % ", ".join(keys))
            cache.delete_many(keys, TopologyDiscoveryCheck.NEIGHBOR_CACHE_VERSION)

    def get_confdb(self):
        # Check cached value
        if hasattr(self, "confdb"):
            return self.confdb
        # Check artefact
        if self.has_artefact("confdb"):
            self.confdb = self.get_artefact("confdb")
            return self.confdb
        # Create
        self.logger.info("Building ConfDB")
        self.confdb = self.object.get_confdb()
        self.set_artefact("confdb", self.confdb)
        return self.confdb


class TopologyDiscoveryCheck(DiscoveryCheck):
    NEIGHBOR_CACHE_VERSION = 1
    # clean_interface settings
    aliased_names_only = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.neighbor_hostname_cache = {}  # (method, id) -> managed object
        self.neighbor_ip_cache = {}  # (method, ip) -> managed object
        self.neighbor_mac_cache = {}  # (method, mac) -> managed object
        self.neighbor_id_cache = {}
        self.interface_aliases = {}  # (object, alias) -> port name
        self._own_mac_check_cache = {}

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        # Check object has interfaces
        if not self.has_capability("DB | Interfaces"):
            self.logger.info("No interfaces has been discovered. Skipping topology check")
            return
        # remote object -> [(local, remote), ..]
        candidates = defaultdict(set)
        loops = {}  # first interface, second interface
        problems = {}
        # Check local side
        ln_key = "mo-neighbors-%s-%s" % (self.name, self.object.id)
        for li, ro, ri in self.cached_neighbors(self.object, ln_key, self.iter_neighbors):
            # Resolve remote object
            remote_object = self.get_neighbor(ro)
            if not remote_object:
                problems[li] = "Remote object '%s' is not found" % str(ro)
                self.logger.info("Remote object '%s' is not found. Skipping", str(ro))
                continue
            # Resolve remote interface name
            remote_interface = self.get_remote_interface(remote_object, ri)
            if not remote_interface:
                problems[li] = "Cannot resolve remote interface %s:%r. Skipping" % (
                    remote_object.name,
                    ri,
                )
                self.logger.info(
                    "Cannot resolve remote interface %s:%r. Skipping", remote_object.name, ri
                )
                continue
            else:
                self.logger.debug("Resolve remote interface as %s:%r", remote_object.name, ri)
            # Detecting loops
            if remote_object.id == self.object.id:
                loops[li] = remote_interface
                if remote_interface in loops and loops[remote_interface] == li:
                    self.logger.info(
                        "Loop link detected: %s:%s - %s:%s",
                        self.object.name,
                        li,
                        self.object.name,
                        remote_interface,
                    )
                    self.confirm_link(self.object, li, remote_object, remote_interface)
                continue
            # Submitting candidates
            self.logger.info(
                "Link candidate: %s:%s - %s:%s",
                self.object.name,
                li,
                remote_object.name,
                remote_interface,
            )
            candidates[remote_object].add((li, remote_interface))
        # Checking candidates from remote side
        for remote_object in candidates:
            if self.allow_asymmetric(remote_object):
                self.logger.info(
                    "Remote object '%s' allowed asymmetric link for method: %s",
                    remote_object.name,
                    self.name,
                )
                remote_neighbors, confirmed = [], candidates[remote_object]
            elif self.required_script and self.required_script not in remote_object.scripts:
                self.logger.info(
                    "Remote object '%s' does not support %s script. Cannot confirm links",
                    remote_object.name,
                    self.required_script,
                )
                continue
            else:
                try:
                    rn_key = "mo-neighbors-%s-%s" % (self.name, remote_object.id)
                    remote_neighbors = self.cached_neighbors(
                        remote_object, rn_key, self.iter_neighbors
                    )
                except Exception as e:
                    self.logger.error(
                        "Cannot get neighbors from candidate %s: %s", remote_object.name, e
                    )
                    self.set_problem(
                        path=list(candidates[remote_object])[0][0],
                        message="Cannot get neighbors from candidate %s: %s"
                        % (remote_object.name, e),
                    )
                    continue
                confirmed = set()
            for li, ro_id, ri in remote_neighbors:
                ro = self.get_neighbor(ro_id)
                if not ro or ro.id != self.object.id:
                    self.logger.debug("Candidates check %s %s %s %s" % (li, ro_id, ro, ri))
                    continue  # To other objects
                remote_interface = self.get_remote_interface(self.object, ri)
                if remote_interface:
                    self.logger.debug("Resolve local interface as %s:%r", self.object.name, ri)
                    confirmed.add((remote_interface, li))
                self.logger.debug(
                    "Candidates: %s, Confirmed: %s", candidates[remote_object], confirmed
                )
            for ll, rr in candidates[remote_object] - confirmed:
                problems[ll] = "Pending link: %s - %s:%s" % (ll, remote_object, rr)
                li = self.clean_interface(self.object, ll)
                if not li:
                    self.logger.info("Cannot clean interface %s:%s. Skipping", self.object, ll)
                    continue
                ri = self.clean_interface(remote_object, rr)
                if not ri:
                    self.logger.info("Cannot clean interface %s:%s. Skipping", remote_object, rr)
                    continue
                self.reject_link(self.object, li, remote_object, ri)
            for ll, rr in candidates[remote_object] & confirmed:
                li = self.clean_interface(self.object, ll)
                if not li:
                    self.logger.info("Cannot clean interface %s:%s. Skipping", self.object, ll)
                    continue
                ri = self.clean_interface(remote_object, rr)
                if not ri:
                    self.logger.info("Cannot clean interface %s:%s. Skipping", remote_object, rr)
                    continue
                self.confirm_link(self.object, li, remote_object, ri)
        if problems:
            for i in problems:
                self.set_problem(path=i, message=problems[i])

    def cached_neighbors(self, mo, key, iter_neighbors):
        """
        Cache iter_neighbors results according to profile settings
        :param mo:
        :param key:
        :param iter_neighbors:
        :return:
        """
        ttl = mo.object_profile.neighbor_cache_ttl
        if not ttl:
            # Disabled cache
            metrics["neighbor_cache_misses"] += 1
            neighbors = iter_neighbors(mo)
            if isinstance(neighbors, types.GeneratorType):
                neighbors = list(iter_neighbors(mo))
            return neighbors
        # Cached version
        neighbors = cache.get(key, version=self.NEIGHBOR_CACHE_VERSION)
        if neighbors is None:
            self.logger.info("Neighbors cache is empty, getting from device...")
            neighbors = iter_neighbors(mo)
            if isinstance(neighbors, types.GeneratorType):
                neighbors = list(iter_neighbors(mo))
            cache.set(key, neighbors, ttl=ttl, version=self.NEIGHBOR_CACHE_VERSION)
            if self.interface_aliases:
                alias_cache = {
                    (mo.id, n[0]): self.interface_aliases[(mo.id, n[0])]
                    for n in neighbors
                    if (mo.id, n[0]) in self.interface_aliases
                }
                cache.set(
                    "%s-aliases" % key, alias_cache, ttl=ttl, version=self.NEIGHBOR_CACHE_VERSION
                )
            metrics["neighbor_cache_misses"] += 1
        else:
            self.logger.info("Use neighbors cache")
            alias_cache = cache.get("%s-aliases" % key, version=self.NEIGHBOR_CACHE_VERSION)
            self.logger.debug("Alias cache is %s", alias_cache)
            if alias_cache:
                self.interface_aliases.update(alias_cache)
            metrics["neighbor_cache_hits"] += 1
        return neighbors

    def iter_neighbors(self, mo):
        """
        Generator yielding all protocol neighbors
        :param mo: Managed object reference
        :returns: yield (local interface, remote id, remote interface)
        """
        return iter(())

    def allow_asymmetric(self, obj) -> bool:
        """Allow asymmetric link"""
        return obj.get_profile().allow_allow_asymmetric_link(self.name)

    def get_neighbor_by_hostname(self, hostname):
        """
        Resolve neighbor by hostname
        """
        hostname = hostname.lower()
        if hostname not in self.neighbor_hostname_cache:
            hosts = DiscoveryID.objects.filter(hostname_id=hostname)[:2]
            n = None
            if len(hosts) == 1:
                n = hosts[0].object
            else:
                # Sometimes, domain part is truncated.
                # Try to resolve anyway
                m = list(
                    DiscoveryID.objects.filter(
                        hostname_id__istartswith=hostname + "." if "." not in hostname else hostname
                    )
                )
                if len(m) == 1:
                    n = m[0].object  # Exact match
            self.neighbor_hostname_cache[hostname] = n
            if n:
                self.neighbor_id_cache[n.id] = n
        return self.neighbor_hostname_cache[hostname]

    get_neighbor = get_neighbor_by_hostname

    def get_neighbor_by_id(self, id):
        """
        Resolve neighbor by managed object's id
        """
        if id not in self.neighbor_id_cache:
            try:
                mo = ManagedObject.objects.get(id=id)
                self.neighbor_id_cache[id] = mo
                self.neighbor_hostname_cache[mo.name] = id
            except ManagedObject.DoesNotExist:
                self.neighbor_id_cache[id] = None
        return self.neighbor_id_cache[id]

    def get_neighbor_by_mac(self, mac):
        """
        Resolve neighbor by hostname
        """
        if mac not in self.neighbor_mac_cache:
            mo = DiscoveryID.find_object_by_mac(mac)
            self.neighbor_mac_cache[mac] = mo
        return self.neighbor_mac_cache[mac]

    def get_neighbor_by_ip(self, ip):
        """
        Resolve neighbor by hostname
        """
        if ip not in self.neighbor_ip_cache:
            mo = DiscoveryID.find_object_by_ip(ip)
            self.neighbor_ip_cache[ip] = mo
        return self.neighbor_ip_cache[ip]

    def get_remote_interface(self, remote_object: ManagedObject, remote_interface: str) -> str:
        """
        Return normalized remote interface name
        May return aliases name which can be finally resolved
        during clean interface
        """
        return remote_object.get_profile().convert_interface_name(remote_interface)

    def clean_interface(self, object, interface):
        """
        Finaly clean interface name:
        * Check for interface alias
        * When aliased_names_only is not set - use local name
        :param object: ManagedObject instance
        :param interface: interface name
        :return: Interface name or None if interface cannot be cleaned
        """
        i = self.interface_aliases.get((object.id, interface))
        if i:
            return i
        if self.aliased_names_only:
            return None
        return interface

    def confirm_link(
        self,
        local_object: ManagedObject,
        local_interface: str,
        remote_object: ManagedObject,
        remote_interface: str,
    ) -> None:
        self.logger.info(
            "Confirm link: %s:%s -- %s:%s",
            local_object,
            local_interface,
            remote_object,
            remote_interface,
        )
        # Get interfaces
        li = self.get_interface_by_name(mo=local_object, name=local_interface)
        if not li:
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. " "Interface %s:%s is not discovered",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
                local_object.name,
                local_interface,
            )
            return
        ri = self.get_interface_by_name(mo=remote_object, name=remote_interface)
        if not ri:
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. " "Interface %s:%s is not discovered",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
                remote_object.name,
                remote_interface,
            )
            return
        self.confirm_interface_link(li, ri)

    def confirm_interface_link(self, li: Interface, ri: Interface) -> None:
        """
        Confirm links between interfaces
        """
        local_object = li.managed_object
        local_interface = li.name
        remote_object = ri.managed_object
        remote_interface = ri.name
        # Check LAGs
        if (
            li.type == "aggregated"
            and ri.type != "aggregated"
            and not li.profile.allow_lag_mismatch
        ):
            self.logger.error(
                "Cannot connect aggregated interface %s:%s to non-aggregated %s:%s",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )
            return
        if (
            ri.type == "aggregated"
            and li.type != "aggregated"
            and not ri.profile.allow_lag_mismatch
        ):
            self.logger.error(
                "Cannot connect aggregated interface %s:%s to non-aggregated %s:%s",
                remote_object.name,
                remote_interface,
                local_object.name,
                local_interface,
            )
            return
        if ri.type == "aggregated" and li.type == "aggregated":
            lic = li.lag_members.count()
            ric = ri.lag_members.count()
            if lic != ric:
                self.logger.error("Cannot connect. LAG size mismatch: %s vs %s", lic, ric)
                return
        # Get existing links
        llink = li.link
        rlink = ri.link
        # Check link is already exists
        if llink and rlink and llink.id == rlink.id:
            self.logger.info(
                "Already linked: %s:%s -- %s:%s via %s",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
                llink.discovery_method,
            )
            if llink.discovery_method != self.name and (
                llink.discovery_method is None
                or self.is_preferable_over(local_object, remote_object, llink)
            ):
                # Change disovery method
                self.logger.info("Remarking discovery method as %s", self.name)
                llink.touch(self.name)
            else:
                # Change last seen
                llink.touch()
            return
        # Check method preferences
        if llink:
            if self.is_preferable_over(local_object, remote_object, llink):
                self.logger.info(
                    "Relinking %s: %s method is preferable over %s",
                    llink,
                    self.name,
                    llink.discovery_method,
                )
            else:
                self.logger.info(
                    "Not linking: %s:%s -- %s:%s. '%s' method is preferable over '%s'",
                    local_object.name,
                    local_interface,
                    remote_object.name,
                    remote_interface,
                    llink.discovery_method,
                    self.name,
                )
                return
        if rlink:
            if self.is_preferable_over(local_object, remote_object, rlink):
                self.logger.info(
                    "Relinking %s: %s method is preferable over %s",
                    rlink,
                    self.name,
                    rlink.discovery_method,
                )
            else:
                self.logger.info(
                    "Not linking: %s:%s -- %s:%s. '%s' method is preferable over '%s'",
                    local_object.name,
                    local_interface,
                    remote_object.name,
                    remote_interface,
                    rlink.discovery_method,
                    self.name,
                )
                return
        # Get interface discovery policies
        # Possible values are:
        # * I - Ignore links, all discovered links rejected
        # * O - Link created only if not exists
        # * R - Existing link will be replaced
        # * C - Link will be attached to cloud
        lpolicy = li.profile.discovery_policy
        rpolicy = ri.profile.discovery_policy
        self.logger.info("Interface linking policy: %s/%s", lpolicy, rpolicy)
        # Check if either policy set to ignore
        if lpolicy == "I" or rpolicy == "I":
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. 'Ignore' interface discovery policy set",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )
            return
        # Check if either side has *Create new* policy and
        # already linked
        if (lpolicy == "O" and llink) or (lpolicy == "O" and llink):
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. "
                "'Create new' interface discovery policy set and "
                "interface is already linked",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )
            return
        # Do not allow merging clouds
        if lpolicy == "C" and rpolicy == "C":
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. Cloud merging is forbidden",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )
            return
        # Get currently linked ends policies
        if llink:
            rri = [i for i in llink.interfaces if i.id != li.id][0]
            lrpolicy = rri.profile.discovery_policy
        else:
            lrpolicy = None
        if rlink:
            rri = [i for i in rlink.interfaces if i.id != ri.id][0]
            rrpolicy = rri.profile.discovery_policy
        else:
            rrpolicy = None
        # *Create new* policy blocks other side relinking
        if lrpolicy == "O" or rrpolicy == "O":
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. Blocked by 'Create new' policy on existing link",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )
            return
        #
        if lpolicy in ("O", "R") and rpolicy in ("O", "R"):
            # Unlink when necessary
            if llink:
                try:
                    li.unlink()
                except ValueError as e:
                    self.logger.info("Failed to unlink %s: %s" % (llink, e))
                    return
            if rlink:
                try:
                    ri.unlink()
                except ValueError as e:
                    self.logger.info("Failed to unlink %s: %s" % (llink, e))
                    return
            self.logger.info(
                "Linking: %s:%s -- %s:%s",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )
            try:
                li.link_ptp(ri, method=self.name)
            except ValueError as e:
                self.logger.info(
                    "Cannot link %s:%s -- %s:%s: %s",
                    local_object.name,
                    local_interface,
                    remote_object.name,
                    remote_interface,
                    e,
                )
            return
        #
        if lpolicy == "C":
            if rlink:
                if rpolicy == "O":
                    self.logger.info(
                        "Not linking: %s:%s -- %s:%s. "
                        "Already linked. "
                        "Connecting to cloud is forbidden by policy",
                        local_object.name,
                        local_interface,
                        remote_object.name,
                        remote_interface,
                    )
                    return
                else:
                    self.logger.info("Unlinking %s", ri)
                    try:
                        ri.unlink()
                    except ValueError as e:
                        self.logger.error("Failed to unlink %s: %s", ri, e)
                        return
            if llink:
                # Attach to existing cloud
                llink.interfaces = llink.interfaces + [ri]
                llink.save()
            else:
                # Create p2p link
                try:
                    li.link_ptp(ri, method=self.name)
                except ValueError as e:
                    self.logger.info(
                        "Cannot link %s:%s -- %s:%s: %s",
                        local_object.name,
                        local_interface,
                        remote_object.name,
                        remote_interface,
                        e,
                    )
                return
        if rpolicy == "C":
            if llink:
                if lpolicy == "O":
                    self.logger.info(
                        "Not linking: %s:%s -- %s:%s. "
                        "Already linked. "
                        "Connecting to cloud is forbidden by policy",
                        local_object.name,
                        local_interface,
                        remote_object.name,
                        remote_interface,
                    )
                    return
                else:
                    self.logger.info("Unlinking %s", li)
                    li.unlink()
            if rlink:
                # Attach to existing cloud
                rlink.interfaces = rlink.interfaces + [li]
                rlink.save()
            else:
                # Create p2p link
                try:
                    ri.link_ptp(li, method=self.name)
                except ValueError as e:
                    self.logger.info(
                        "Cannot link %s:%s -- %s:%s: %s",
                        local_object.name,
                        local_interface,
                        remote_object.name,
                        remote_interface,
                        e,
                    )
                return
        #
        self.logger.info(
            "Not linking: %s:%s -- %s:%s. " "Link creating not allowed",
            local_object.name,
            local_interface,
            remote_object.name,
            remote_interface,
        )

    def reject_link(self, local_object, local_interface, remote_object, remote_interface):
        self.logger.info(
            "Reject link: %s:%s -- %s:%s",
            local_object,
            local_interface,
            remote_object,
            remote_interface,
        )
        # Get interfaces
        li = self.get_interface_by_name(mo=local_object, name=local_interface)
        if not li:
            self.logger.info(
                "Cannot unlink: %s:%s -- %s:%s. Interface %s:%s is not discovered",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
                local_object.name,
                local_interface,
            )
            return
        ri = self.get_interface_by_name(mo=remote_object, name=remote_interface)
        if not ri:
            self.logger.info(
                "Cannot unlink: %s:%s -- %s:%s. Interface %s:%s is not discovered",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
                remote_object.name,
                remote_interface,
            )
            return
        # Get existing links
        llink = li.link
        rlink = ri.link
        # Check link is already exists
        if llink and rlink and llink.id == rlink.id:
            if llink.discovery_method == self.name:
                self.logger.info(
                    "Unlinking: %s:%s -- %s:%s. ",
                    local_object.name,
                    local_interface,
                    remote_object.name,
                    remote_interface,
                )
                llink.delete()
            else:
                self.logger.info(
                    "Cannot unlink: %s:%s -- %s:%s. Created by other discovery method (%s)",
                    local_object.name,
                    local_interface,
                    remote_object.name,
                    remote_interface,
                    llink.discovery_method,
                )
        else:
            self.logger.info(
                "Cannot unlink: %s:%s -- %s:%s. Not linked yet",
                local_object.name,
                local_interface,
                remote_object.name,
                remote_interface,
            )

    def confirm_cloud(self, root_interface: Interface, interfaces: List[Interface]) -> None:
        """
        Ensure `root_interface` and `interfaces` are connected to same cloud link

        :param root_interface: Root `Interface` of the cloud
        :param interfaces: List of `Interface`
        """
        if not interfaces:
            return
        # get existing links
        links: Dict[Interface, Link] = {}
        for link in Link.objects.filter(
            interfaces__in=[root_interface.id] + [i.id for i in interfaces]
        ):
            for i in link.interfaces:
                links[i] = link
        # Get or create cloud
        root_link = links.get(root_interface)
        if root_link:
            if root_link.discovery_method != self.name:
                if not self.object.segment.profile.is_preferable_method(
                    self.name, root_link.discovery_method
                ):
                    self.logger.info(
                        "Cannot create cloud on %s:%s. Existing method '%s' is preferable over '%s'",
                        root_interface.managed_object.name,
                        root_interface.name,
                        root_link.discovery_method,
                        self.name,
                    )
                    return
                self.logger.info(
                    "Changing cloud on %s:%s method to %s",
                    root_interface.managed_object.name,
                    root_interface.name,
                    self.name,
                )
                root_link.discovery_method = self.name
            else:
                self.logger.info(
                    "Using existent cloud on %s:%s",
                    root_interface.managed_object.name,
                    root_interface.name,
                )
        else:
            # Create one
            self.logger.info(
                "Creating cloud on %s:%s", root_interface.managed_object.name, root_interface.name
            )
            root_link = Link(interfaces=[root_interface], discovery_method=self.name)
        # Check all interfaces
        for iface in interfaces:
            if_link = links.get(iface)
            if if_link:
                if if_link.id == root_link.id:
                    self.logger.info(
                        "%s:%s is already linked", iface.managed_object.name, iface.name
                    )
                    continue
                elif not self.object.segment.profile.is_preferable_method(
                    self.name, if_link.discovery_method
                ):
                    self.logger.info(
                        "Cannot unlink %s:%s. Method %s is preferable over %s",
                        iface.managed_object.name,
                        iface.name,
                        if_link.discovery_method,
                        self.name,
                    )
                    continue
                else:
                    self.logger.info(
                        "Relinking %s:%s to cloud %s:%s",
                        iface.managed_object.name,
                        iface.name,
                        root_interface.managed_object.name,
                        root_interface.name,
                    )
                    iface.unlink()
                    root_link.interfaces += [iface]
            else:
                self.logger.info(
                    "Linking %s:%s to cloud %s:%s",
                    iface.managed_object.name,
                    iface.name,
                    root_interface.managed_object.name,
                    root_interface.name,
                )
                root_link.interfaces += [iface]
        root_link.save()

    def is_preferable_over(self, mo1, mo2, link):
        """
        Check current discovery method is preferable over link's one
        :param mo1: Local managed object
        :param mo2: Remote managed object
        :param link: Existing ling
        :returns: True, if check's method is preferabble
        """
        if mo1.segment == mo2.segment or mo2.segment.id not in mo1.segment.get_path():
            # Same segment, or mo1 is in upper segment. apply local segment policy
            return mo1.segment.profile.is_preferable_method(self.name, link.discovery_method)
        # mo2 is in upper segment, use remote segment policy
        return mo2.segment.profile.is_preferable_method(self.name, link.discovery_method)

    def set_interface_alias(self, object, interface_name, alias):
        """
        Set interface alias
        Aliases will be finally resolved by clean_interface
        :param object:
        :param interface_name:
        :param alias:
        :return:
        """
        self.interface_aliases[object.id, alias] = interface_name

    @cachetools.cachedmethod(operator.attrgetter("_own_mac_check_cache"))
    def is_own_mac(self, mac):
        mr = DiscoveryID.macs_for_objects(self.object)
        return mr and any(1 for f, t in mr if f <= mac <= t)


class PolicyDiscoveryCheck(DiscoveryCheck):
    policy_name = None
    policy_map = {
        "s": ["script"],
        "S": ["script", "confdb"],
        "C": ["confdb", "script"],
        "c": ["confdb"],
    }

    def get_policy(self):
        """
        Get effective policy
        :return:
        """
        if self.policy_name:
            return getattr(self.object, self.policy_name)()
        raise NotImplementedError

    def get_data(self):
        """
        Request data according to policy (Either from equipment of from ConfDB)
        :return:
        """
        for method in self.policy_map[self.get_policy()]:
            check = getattr(self, "can_get_data_from_%s" % method)
            if not check():
                continue
            getter = getattr(self, "request_data_from_%s" % method)
            data = getter()
            if data is not None:
                return data
        return None

    def request_data_from_script(self):
        self.logger.info("Requesting data from device")
        return self.get_data_from_script()

    def get_data_from_script(self):
        """
        Actually get data from script. Should be overriden
        :return:
        """
        return None

    def can_get_data_from_script(self):
        """
        Check if object has all prerequisites to get data from script
        :return:
        """
        if self.required_script not in self.object.scripts:
            self.logger.info("%s script is not supported. Skipping", self.required_script)
            return False
        return True

    def request_data_from_confdb(self):
        # self.confdb is set by can_get_data_from_confdb
        return self.get_data_from_confdb()

    def get_data_from_confdb(self):
        """
        Actually get data from ConfDB. Should be overriden
        :return:
        """
        return None

    def can_get_data_from_confdb(self):
        """
        Check if object has all prerequisites to get data from ConfDB
        :return:
        """
        confdb = self.get_confdb()
        if confdb is None:
            self.logger.error("confdb artefact is not set. Skipping")
            return False
        return True

    def has_required_script(self):
        return super().has_required_script() or self.get_policy() != ["script"]
