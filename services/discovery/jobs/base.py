#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Basic MO discovery job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import contextlib
import time
import zlib
import datetime
# Third-party modules
import bson
import six
from six.moves import StringIO
# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.debug import error_report
from noc.core.log import PrefixLoggerAdapter
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.lib.nosql import get_db
from noc.core.service.error import RPCError, RPCRemoteError
from noc.core.service.loader import get_service
from noc.core.error import (
    ERR_CLI_AUTH_FAILED, ERR_CLI_NO_SUPER_COMMAND,
    ERR_CLI_LOW_PRIVILEGES, ERR_CLI_SSH_PROTOCOL_ERROR,
    ERR_CLI_CONNECTION_REFUSED
)
from noc.core.span import Span
from noc.core.error import ERR_UNKNOWN


class MODiscoveryJob(PeriodicJob):
    model = ManagedObject
    use_get_by_id = True
    use_offset = True
    # Name of umbrella class to cover discovery problems
    umbrella_cls = None

    def __init__(self, *args, **kwargs):
        super(MODiscoveryJob, self).__init__(*args, **kwargs)
        self.out_buffer = StringIO()
        self.logger = PrefixLoggerAdapter(
            self.logger,
            "",
            target=self.out_buffer
        )
        self.check_timings = []
        self.problems = []
        self.caps = None
        self.has_fatal_error = False
        self.service = self.scheduler.service

    def schedule_next(self, status):
        if self.check_timings:
            self.logger.info("Timings: %s", ", ".join(
                "%s = %.2fms" % (n, t * 1000) for n, t in self.check_timings
            ))
        super(MODiscoveryJob, self).schedule_next(status)
        # Update alarm statuses
        self.update_alarms()
        # Write job log
        key = "discovery-%s-%s" % (
            self.attrs[self.ATTR_CLASS],
            self.attrs[self.ATTR_KEY]
        )
        problems = {}
        for p in self.problems:
            if p["check"] in problems and p["path"]:
                problems[p["check"]][p["path"]] = p["message"]
            elif p["check"] in problems and not p["path"]:
                # p["path"] == ""
                problems[p["check"]][p["path"]] += "; %s" % p["message"]
            else:
                problems[p["check"]] = {p["path"]: p["message"]}
        get_db()["noc.joblog"].update({
            "_id": key
        }, {
            "$set": {
                "log": bson.Binary(zlib.compress(self.out_buffer.getvalue())),
                "problems": problems
            }
        }, upsert=True)

    def can_run(self):
        # @todo: Make configurable
        os = self.object.get_status()
        if not os:
            self.logger.info("Object ping Fail, Job will not run")
        return self.object.is_managed and os

    @contextlib.contextmanager
    def check_timer(self, name):
        t = time.time()
        yield
        self.check_timings += [(name, time.time() - t)]

    def set_problem(self, check=None, alarm_class=None, path=None,
                    message=None, fatal=False):
        """
        Set discovery problem
        :param check: Check name
        :param alarm_class: Alarm class instance or name
        :param path: Additional path
        :param message: Text message
        :param fatal: True if problem is fatal and all following checks
            must be disabled
        :return:
        """
        self.problems += [{
            "check": check,
            "alarm_class": alarm_class,
            # in MongoDB Key must be string
            "path": str(path) if path else "",
            "message": message,
            "fatal": fatal
        }]
        if fatal:
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
        return bool(self.get_caps().get("Management | Allow Sessions"))

    def update_umbrella(self, umbrella_cls, details):
        """
        Update umbrella alarm status for managed object

        :param umbrella_cls: Umbrella alarm class (AlarmClass instance)
        :param details: List of dicts, containing
            * alarm_class - Detail alarm class
            * path - Additional path
            * severity - Alarm severity
            * vars - dict of alarm vars
        :return:
        """
        from noc.fm.models.activealarm import ActiveAlarm

        now = datetime.datetime.now()
        umbrella = ActiveAlarm.objects.filter(
            alarm_class=umbrella_cls.id,
            managed_object=self.object.id
        ).first()
        u_sev = sum(d.get("severity", 0) for d in details)
        if not umbrella and not details:
            # No money, no honey
            return
        elif not umbrella and details:
            # Open new umbrella
            umbrella = ActiveAlarm(
                timestamp=now,
                managed_object=self.object.id,
                alarm_class=umbrella_cls.id,
                severity=u_sev
            )
            umbrella.save()
            self.logger.info("Opening umbrella alarm %s (%s)",
                             umbrella.id, umbrella_cls.name)
        elif umbrella and not details:
            # Close existing umbrella
            self.logger.info("Clearing umbrella alarm %s (%s)",
                             umbrella.id, umbrella_cls.name)
            umbrella.clear_alarm("Closing umbrella")
        elif umbrella and details and u_sev != umbrella.severity:
            self.logger.info(
                "Change umbrella alarm %s severity %s -> %s (%s)",
                umbrella.id, umbrella.severity, u_sev,
                umbrella_cls.name
            )
            umbrella.change_severity(severity=u_sev)
        # Get existing details for umbrella
        active_details = {}  # (alarm class, path) -> alarm
        if umbrella:
            for da in ActiveAlarm.objects.filter(root=umbrella.id):
                d_path = da.vars.get("path", "")
                active_details[da.alarm_class, d_path] = da
        # Synchronize details
        self.logger.info("Active details: %s" % active_details)
        seen = set()
        for d in details:
            d_path = d.get("path", "")
            d_key = (d["alarm_class"], d_path)
            d_sev = d.get("severity", 0)
            # Key for seen details
            seen.add(d_key)
            if d_key in active_details and active_details[d_key].severity != d_sev:
                # Change severity
                self.logger.info(
                    "Change detail alarm %s severity %s -> %s",
                    active_details[d_key].id,
                    active_details[d_key].severity,
                    d_sev
                )
                active_details[d_key].change_severity(severity=d_sev)
            elif d_key not in active_details:
                # Create alarm
                self.logger.info("Create detail alarm to path %s",
                                 d_key)
                v = d.get("vars", {})
                v["path"] = d_path
                da = ActiveAlarm(
                    timestamp=now,
                    managed_object=self.object.id,
                    alarm_class=d["alarm_class"],
                    severity=d_sev,
                    vars=v,
                    root=umbrella.id
                )
                da.save()
                self.logger.info("Opening detail alarm %s %s (%s)",
                                 da.id, d_path, da.alarm_class.name)
        # Close details when necessary
        for d in set(active_details) - seen:
            self.logger.info("Clearing detail alarm %s",
                             active_details[d].id)
            active_details[d].clear_alarm("Closing")

    def update_alarms(self):
        from noc.fm.models.alarmseverity import AlarmSeverity
        from noc.fm.models.alarmclass import AlarmClass

        prev_status = self.context.get("umbrella_settings", False)
        current_status = self.can_update_alarms()
        self.context["umbrella_settings"] = current_status

        if not prev_status and not current_status:
            return
        self.logger.info("Updating alarm statuses")
        umbrella_cls = AlarmClass.get_by_name(self.umbrella_cls)
        if not umbrella_cls:
            self.logger.info("No umbrella alarm class. Alarm statuses not updated")
            return
        details = []
        if current_status:
            fatal_weight = self.get_fatal_alarm_weight()
            weight = self.get_alarm_weight()
            for p in self.problems:
                if not p["alarm_class"]:
                    continue
                ac = AlarmClass.get_by_name(p["alarm_class"])
                if not ac:
                    self.logger.info("Unknown alarm class %s. Skipping",
                                     p["alarm_class"])
                    continue
                details += [{
                    "alarm_class": ac,
                    "path": p["path"],
                    "severity": AlarmSeverity.severity_for_weight(
                        fatal_weight if p["fatal"] else weight),
                    "vars": {
                        "path": p["path"],
                        "message": p["message"]
                    }
                }]
        else:
            # Clean up all open alarms as they has been disabled
            details = []
        self.update_umbrella(umbrella_cls, details)

    def can_update_alarms(self):
        return False

    def get_fatal_alarm_weight(self):
        return 1

    def get_alarm_weight(self):
        return 1


class DiscoveryCheck(object):
    name = None
    # If not none, check required script is available
    # before running check
    required_script = None
    # If not none, check object has all required capablities
    # from list
    required_capabilities = None
    #
    fatal_errors = set([
        ERR_CLI_AUTH_FAILED,
        ERR_CLI_NO_SUPER_COMMAND,
        ERR_CLI_LOW_PRIVILEGES,
        ERR_CLI_CONNECTION_REFUSED,
        ERR_CLI_SSH_PROTOCOL_ERROR
    ])
    # Error -> Alarm class mappings
    error_map = {
        ERR_CLI_AUTH_FAILED: "Discovery | Error | Auth Failed",
        ERR_CLI_NO_SUPER_COMMAND: "Discovery | Error | No Super",
        ERR_CLI_LOW_PRIVILEGES: "Discovery | Error | Low Privileges",
        ERR_CLI_CONNECTION_REFUSED: "Discovery | Error | Connection Refused",
        ERR_CLI_SSH_PROTOCOL_ERROR: "Discovery | Error | SSH Protocol"
    }

    def __init__(self, job):
        self.service = job.service
        self.job = job
        self.object = self.job.object
        self.logger = self.job.logger.get_logger(
            "[%s" % self.name
        )
        self.if_name_cache = {}  # mo, name -> Interface
        self.if_mac_cache = {}  # mo, mac -> Interface
        self.if_ip_cache = {}
        self.sub_cache = {}
        self.profile_cache = {}

    def is_enabled(self):
        checks = self.job.attrs.get("_checks", set())
        return not checks or self.name in checks

    def has_fatal_error(self):
        return self.job.has_fatal_error

    def has_required_script(self):
        return (not self.required_script or
                self.required_script in self.object.scripts)

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
                self.logger.info(
                    "Object hasn't required capability '%s'. "
                    "Skipping",
                    cn
                )
                return False
            v = caps[cn]
            if not v:
                self.logger.info(
                    "Capability '%s' is disabled. Skipping",
                    cn
                )
                return False
        return True

    def run(self):
        if not self.is_enabled():
            self.logger.info("Check is disabled. Skipping")
            return
        if self.has_fatal_error():
            self.logger.info("Check is disabled due to previous fatal error. Skipping")
            return
        with Span(server="discovery", service=self.name) as span, self.job.check_timer(self.name):
            # Check required scripts
            if not self.has_required_script():
                self.logger.info("%s script is not supported. Skipping",
                                 self.required_script)
                return
            # Check required capabilities
            if not self.has_required_capabilities():
                return
            # Run check
            try:
                self.handler()
            except RPCRemoteError as e:
                self.logger.error(
                    "RPC Remote error (%s): %s",
                    e.remote_code, e)
                if e.remote_code:
                    message = "Remote error code %s" % e.remote_code
                else:
                    message = "Remote error code %s, message: %s" % (e.remote_code, e)
                self.set_problem(
                    alarm_class=self.error_map.get(e.remote_code),
                    message=message,
                    fatal=e.remote_code in self.fatal_errors
                )
                span.error_code = e.remote_code
                span.error_text = str(e)
            except RPCError as e:
                self.set_problem(
                    alarm_class=self.error_map.get(e.default_code),
                    message="RPC Error: %s" % e,
                    fatal=e.default_code in self.fatal_errors
                )
                self.logger.error("Terminated due RPC error: %s", e)
                span.error_code = e.default_code
                span.error_text = str(e)
            except Exception as e:
                self.set_problem(
                    alarm_class="Discovery | Error | Unhandled Exception",
                    message="Unhandled exception: %s" % e
                )
                error_report(logger=self.logger)
                span.error_code = ERR_UNKNOWN
                span.error_text = str(e)

    def handler(self):
        pass

    def update_if_changed(self, obj, values, ignore_empty=None,
                          async=False, bulk=None):
        """
        Update fields if changed.
        :param obj: Document instance
        :type obj: Document
        :param values: New values
        :type values: dict
        :param ignore_empty: List of fields which may be ignored if empty
        :param async: set write concern to 0
        :param bulk: Execute as the bulk op instead
        :returns: List of changed (key, value)
        :rtype: list
        """
        changes = []
        ignore_empty = ignore_empty or []
        for k, v in six.iteritems(values):
            vv = getattr(obj, k)
            if v != vv:
                if type(v) != int or not hasattr(vv, "id") or v != vv.id:
                    if k in ignore_empty and (v is None or v == ""):
                        continue
                    setattr(obj, k, v)
                    changes += [(k, v)]
        if changes:
            if bulk:
                op = {
                    "$set": dict(changes)
                }
                id_field = obj._fields[Interface._meta["id_field"]].db_field
                bulk.find({
                    id_field: obj.pk
                }).update(op)
            else:
                kwargs = {}
                if async:
                    kwargs["write_concern"] = {"w": 0}
                obj.save(**kwargs)
        return changes

    def log_changes(self, msg, changes):
        """
        Log changes
        :param msg: Message
        :type msg: str
        """
        if changes:
            self.logger.info("%s: %s" % (
                msg, ", ".join("%s = %s" % (k, v) for k, v in changes)))

    def get_interface_by_name(self, name, mo=None):
        """
        Returns Interface instance
        """
        mo = mo or self.object
        name = mo.get_profile().convert_interface_name(name)
        self.logger.debug("Searching port by name: %s:%s", mo.name, name)
        key = (mo, name)
        if key not in self.if_name_cache:
            i = Interface.objects.filter(
                managed_object=mo,
                name=name
            ).first()
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
            li = list(Interface.objects.filter(
                managed_object=mo,
                mac=mac,
                type="physical"
            ))
            if len(li) == 1:
                li = li[0]
            else:
                li = None  # Non unique or not found
            self.if_mac_cache[key] = li
        return self.if_mac_cache[key]

    def get_interface_by_ip(self, ip, mo=None):
        """
        Returns Interface instance referred by IP address
        """
        mo = mo or self.object
        self.logger.debug("Searching port by IP: %s:%s", mo.name, ip)
        key = (mo, ip)
        if key not in self.if_ip_cache:
            li = list(Interface.objects.filter(
                managed_object=self.object.id,
                ipv4_addresses__startswith="%s/" % ip,
                type="physical"
            ))
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
            si = SubInterface.objects.filter(
                interface=interface.id, name=name).first()
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
            managed_object=self.object.id,
            type__in=["physical", "aggregated"]
        ):
            l = i.link
            if l:
                self.logger.info("Unlinking: %s", l)
                try:
                    i.unlink()
                except ValueError as e:
                    self.logger.info("Failed to unlink: %s", e)

    def set_problem(self, alarm_class=None, path=None,
                    message=None, fatal=False):
        """
        Set discovery problem
        :param alarm_class: Alarm class instance or name
        :param path: Additional path
        :param message: Text message
        :param fatal: True if problem is fatal and all following checks
            must be disabled
        :return:
        """
        self.logger.info("Set path: %s" % path)
        self.job.set_problem(
            check=self.name,
            alarm_class=alarm_class,
            path=path,
            message=message,
            fatal=fatal
        )


class TopologyDiscoveryCheck(DiscoveryCheck):
    def __init__(self, *args, **kwargs):
        super(TopologyDiscoveryCheck, self).__init__(*args, **kwargs)
        self.neighbor_hostname_cache = {}  # (method, id) -> managed object
        self.neighbor_ip_cache = {}  # (method, ip) -> managed object
        self.neighbor_mac_cache = {}  # (method, mac) -> managed object
        self.neighbor_id_cache = {}
        self.interface_aliases = {}  # (object, alias) -> port name

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        # remote object -> [(local, remote), ..]
        candidates = defaultdict(set)
        loops = {}  # first interface, second interface
        problems = {}
        # Check local side
        for li, ro, ri in self.iter_neighbors(self.object):
            # Resolve remote object
            remote_object = self.get_neighbor(ro)
            if not remote_object:
                problems[li] = "Remote object '%s' is not found" % str(ro)
                self.logger.info(
                    "Remote object '%s' is not found. Skipping",
                    str(ro)
                )
                continue
            # Resolve remote interface name
            remote_interface = self.get_remote_interface(
                remote_object,
                ri
            )
            if not remote_interface:
                problems[li] = "Cannot resolve remote interface %s:%r. Skipping" % (remote_object.name, ri)
                self.logger.info(
                    "Cannot resolve remote interface %s:%r. Skipping",
                    remote_object.name, ri
                )
                continue
            else:
                self.logger.debug(
                    "Resolve remote interface as %s:%r",
                    remote_object.name, ri
                )
            # Detecting loops
            if remote_object.id == self.object.id:
                loops[li] = remote_interface
                if (remote_interface in loops and loops[remote_interface] == li):
                    self.logger.info(
                        "Loop link detected: %s:%s - %s:%s",
                        self.object.name, li,
                        self.object.name, remote_interface)
                    self.confirm_link(
                        self.object, li,
                        remote_object, remote_interface
                    )
                continue
            # Submitting candidates
            self.logger.info(
                "Link candidate: %s:%s - %s:%s",
                self.object.name, li,
                remote_object.name, remote_interface
            )
            candidates[remote_object].add((li, remote_interface))

        # Checking candidates from remote side
        for remote_object in candidates:
            if (self.required_script and
                    self.required_script not in remote_object.scripts):
                self.logger.info(
                    "Remote object '%s' does not support %s script. "
                    "Cannot confirm links",
                    remote_object.name, self.required_script
                )
                continue
            try:
                remote_neighbors = list(
                    self.iter_neighbors(remote_object)
                )
            except Exception as e:
                self.logger.error(
                    "Cannot get neighbors from candidate %s: %s",
                    remote_object.name,
                    e
                )
                self.set_problem(
                    path=list(candidates[remote_object])[0][0],
                    message="Cannot get neighbors from candidate %s: %s" % (
                        remote_object.name, e)
                )
                continue
            confirmed = set()
            for li, ro_id, ri in remote_neighbors:
                ro = self.get_neighbor(ro_id)
                if not ro or ro.id != self.object.id:
                    self.logger.debug("Candidates check %s %s %s %s" % (li, ro_id, ro, ri))
                    continue  # To other objects
                remote_interface = self.get_remote_interface(
                    self.object,
                    ri
                )
                if remote_interface:
                    self.logger.debug(
                        "Resolve local interface as %s:%r",
                        self.object.name, ri
                    )
                    confirmed.add((remote_interface, li))
                self.logger.debug(
                    "Candidates: %s, Confirmed: %s",
                    candidates[remote_object],
                    confirmed
                )
            for l, r in candidates[remote_object] - confirmed:
                problems[l] = "Pending link: %s - %s:%s" % (l, remote_object, r)
                li = self.clean_interface(self.object, l)
                if not li:
                    self.logger.info(
                        "Cannot clean interface %s:%s. Skipping",
                        self.object, l)
                    continue
                ri = self.clean_interface(self.object, r)
                if not ri:
                    self.logger.info(
                        "Cannot clean interface %s:%s. Skipping",
                        remote_object, r)
                    continue
                self.reject_link(
                    self.object, li,
                    remote_object, ri
                )
            for l, r in candidates[remote_object] & confirmed:
                li = self.clean_interface(self.object, l)
                if not li:
                    self.logger.info(
                        "Cannot clean interface %s:%s. Skipping",
                        self.object, l)
                    continue
                ri = self.clean_interface(remote_object, r)
                if not ri:
                    self.logger.info(
                        "Cannot clean interface %s:%s. Skipping",
                        remote_object, r)
                    continue
                self.confirm_link(
                    self.object, li,
                    remote_object, ri
                )
        if problems:
            for i in problems:
                self.set_problem(
                    path=i,
                    message=problems[i]
                )

    def iter_neighbors(self, mo):
        """
        Generator yielding all protocol neighbors
        :param mo: Managed object reference
        :returns: yield (local interface, remote id, remote interface)
        """
        raise StopIteration()

    def get_neighbor_by_hostname(self, hostname):
        """
        Resolve neighbor by hostname
        """
        if hostname not in self.neighbor_hostname_cache:
            n = DiscoveryID.objects.filter(hostname=hostname).first()
            if n:
                n = n.object
            elif "." not in hostname:
                # Sometimes, domain part is truncated.
                # Try to resolve anyway
                m = list(DiscoveryID.objects.filter(
                    hostname__startswith=hostname + "."))
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
            mo = DiscoveryID.find_object(mac=mac)
            self.neighbor_mac_cache[mac] = mo
        return self.neighbor_mac_cache[mac]

    def get_neighbor_by_ip(self, ip):
        """
        Resolve neighbor by hostname
        """
        if ip not in self.neighbor_ip_cache:
            mo = DiscoveryID.find_object(ipv4_address=ip)
            self.neighbor_ip_cache[ip] = mo
        return self.neighbor_ip_cache[ip]

    def get_remote_interface(self, remote_object, remote_interface):
        """
        Return normalized remote interface name
        May return aliases name which can be finally resolved
        during clean interface
        """
        return remote_object.get_profile().convert_interface_name(
            remote_interface
        )

    def clean_interface(self, object, interface):
        """
        Finaly clean interface name
        And convert to local conventions
        :param object:
        :param interface:
        :return: Interface name or None if interface cannot be cleaned
        """
        return self.interface_aliases.get((object, interface), interface)

    def confirm_link(self, local_object, local_interface,
                     remote_object, remote_interface):
        self.logger.info(
            "Confirm link: %s:%s -- %s:%s",
            local_object, local_interface,
            remote_object, remote_interface
        )
        # Get interfaces
        li = self.get_interface_by_name(mo=local_object,
                                        name=local_interface)
        if not li:
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. "
                "Interface %s:%s is not discovered",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
                local_object.name, local_interface
            )
            return
        ri = self.get_interface_by_name(mo=remote_object,
                                        name=remote_interface)
        if not ri:
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. "
                "Interface %s:%s is not discovered",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
                remote_object.name, remote_interface
            )
            return
        # Check LAGs
        if li.type == "aggregated" and ri.type != "aggregated" and not li.profile.allow_lag_mismatch:
            self.logger.error(
                "Cannot connect aggregated interface %s:%s to non-aggregated %s:%s",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        if ri.type == "aggregated" and li.type != "aggregated" and not ri.profile.allow_lag_mismatch:
            self.logger.error(
                "Cannot connect aggregated interface %s:%s to non-aggregated %s:%s",
                remote_object.name, remote_interface,
                local_object.name, local_interface
            )
            return
        if ri.type == "aggregated" and li.type == "aggregated":
            lic = li.lag_members.count()
            ric = ri.lag_members.count()
            if lic != ric:
                self.logger.error(
                    "Cannot connect. LAG size mismatch: %s vs %s",
                    lic, ric
                )
                return
        # Get existing links
        llink = li.link
        rlink = ri.link
        # Check link is already exists
        if llink and rlink and llink.id == rlink.id:
            self.logger.info(
                "Already linked: %s:%s -- %s:%s via %s",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
                llink.discovery_method
            )
            if (
                llink.discovery_method != self.name and
                (llink.discovery_method is None or
                     self.is_preferable_over(llink.discovery_method))
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
            if self.is_preferable_over(llink.discovery_method):
                self.logger.info(
                    "Relinking %s: %s method is preferable over %s",
                    llink, self.name, llink.discovery_method
                )
            else:
                self.logger.info(
                    "Not linking: %s:%s -- %s:%s. "
                    "'%s' method is preferable over '%s'",
                    local_object.name, local_interface,
                    remote_object.name, remote_interface,
                    llink.discovery_method, self.name
                )
                return
        if rlink:
            if self.is_preferable_over(rlink.discovery_method):
                self.logger.info(
                    "Relinking %s: %s method is preferable over %s",
                    rlink, self.name, rlink.discovery_method
                )
            else:
                self.logger.info(
                    "Not linking: %s:%s -- %s:%s. "
                    "'%s' method is preferable over '%s'",
                    local_object.name, local_interface,
                    remote_object.name, remote_interface,
                    rlink.discovery_method, self.name
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
        self.logger.info(
            "Interface linking policy: %s/%s",
            lpolicy, rpolicy
        )
        # Check if either policy set to ignore
        if lpolicy == "I" or rpolicy == "I":
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. "
                "'Ignore' interface discovery policy set",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        # Check if either side has *Create new* policy and
        # already linked
        if (lpolicy == "O" and llink) or (lpolicy == "O" and llink):
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. "
                "'Create new' interface discovery policy set and "
                "interface is already linked",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        # Do not allow merging clouds
        if lpolicy == "C" and rpolicy == "C":
            self.logger.info(
                "Not linking: %s:%s -- %s:%s. "
                "Cloud merging is forbidden",
                local_object.name, local_interface,
                remote_object.name, remote_interface
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
                "Not linking: %s:%s -- %s:%s. "
                "Blocked by 'Create new' policy on existing link",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        #
        if lpolicy in ("O", "R") and rpolicy in ("O", "R"):
            # Unlink when necessary
            if llink:
                try:
                    li.unlink()
                except ValueError as e:
                    self.logger.info(
                        "Failed to unlink %s: %s" % (llink, e)
                    )
                    return
            if rlink:
                try:
                    ri.unlink()
                except ValueError as e:
                    self.logger.info(
                        "Failed to unlink %s: %s" % (llink, e)
                    )
                    return
            self.logger.info(
                "Linking: %s:%s -- %s:%s",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            try:
                li.link_ptp(ri, method=self.name)
            except ValueError as e:
                self.logger.info(
                    "Cannot link %s:%s -- %s:%s: %s",
                    local_object.name, local_interface,
                    remote_object.name, remote_interface,
                    e
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
                        local_object.name, local_interface,
                        remote_object.name, remote_interface
                    )
                    return
                else:
                    self.logger.info("Unlinking %s", ri)
                    try:
                        ri.unlink()
                    except ValueError as e:
                        self.logger.error(
                            "Failed to unlink %s: %s",
                            ri, e
                        )
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
                        local_object.name, local_interface,
                        remote_object.name, remote_interface,
                        e
                    )
                return
        if rpolicy == "C":
            if llink:
                if lpolicy == "O":
                    self.logger.info(
                        "Not linking: %s:%s -- %s:%s. "
                        "Already linked. "
                        "Connecting to cloud is forbidden by policy",
                        local_object.name, local_interface,
                        remote_object.name, remote_interface
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
                        local_object.name, local_interface,
                        remote_object.name, remote_interface,
                        e
                    )
                return
        #
        self.logger.info(
            "Not linking: %s:%s -- %s:%s. "
            "Link creating not allowed",
            local_object.name, local_interface,
            remote_object.name, remote_interface
        )

    def reject_link(self, local_object, local_interface,
                    remote_object, remote_interface):
        self.logger.info(
            "Reject link: %s:%s -- %s:%s",
            local_object, local_interface,
            remote_object, remote_interface
        )
        # Get interfaces
        li = self.get_interface_by_name(mo=local_object,
                                        name=local_interface)
        if not li:
            self.logger.info(
                "Cannot unlink: %s:%s -- %s:%s. "
                "Interface %s:%s is not discovered",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
                local_object.name, local_interface
            )
            return
        ri = self.get_interface_by_name(mo=remote_object,
                                        name=remote_interface)
        if not ri:
            self.logger.info(
                "Cannot unlink: %s:%s -- %s:%s. "
                "Interface %s:%s is not discovered",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
                remote_object.name, remote_interface
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
                    local_object.name, local_interface,
                    remote_object.name, remote_interface
                )
                llink.delete()
            else:
                self.logger.info(
                    "Cannot unlink: %s:%s -- %s:%s. "
                    "Created by other discovery method (%s)",
                    local_object.name, local_interface,
                    remote_object.name, remote_interface,
                    llink.discovery_method
                )
        else:
            self.logger.info(
                "Cannot unlink: %s:%s -- %s:%s. "
                "Not linked yet",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
            )

    def is_preferable_over(self, method):
        """
        Check current discovery method is preferable over *method*
        """
        return self.job.is_preferable_method(self.name, method)

    def set_interface_alias(self, object, interface_name, alias):
        """
        Set interface alias
        Aliases will be finally resolved by clean_interface
        :param object:
        :param interface_name:
        :param alias:
        :return:
        """
        self.interface_aliases[object, alias] = interface_name
