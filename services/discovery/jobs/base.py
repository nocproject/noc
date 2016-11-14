#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic MO discovery job
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import cStringIO
import contextlib
import time
import zlib
## Third-party modules
import bson
## NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.lib.debug import error_report
from noc.lib.log import PrefixLoggerAdapter
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.lib.nosql import get_db
from noc.core.service.rpc import RPCError


class MODiscoveryJob(PeriodicJob):
    model = ManagedObject
    use_get_by_id = True
    use_offset = True

    def __init__(self, *args, **kwargs):
        super(MODiscoveryJob, self).__init__(*args, **kwargs)
        self.out_buffer = cStringIO.StringIO()
        self.logger = PrefixLoggerAdapter(
            self.logger,
            "",
            target=self.out_buffer
        )
        self.check_timings = []
        self.problems = {}  # check -> problem

    def schedule_next(self, status):
        if self.check_timings:
            self.logger.info("Timings: %s", ", ".join(
                "%s = %.2fms" % (n, t * 1000) for n, t in self.check_timings
            ))
        super(MODiscoveryJob, self).schedule_next(status)
        # Write job log
        key = "discovery-%s-%s" % (
            self.attrs[self.ATTR_CLASS],
            self.attrs[self.ATTR_KEY]
        )
        get_db()["noc.joblog"].update({
            "_id": key
        }, {
            "$set": {
                "log": bson.Binary(zlib.compress(self.out_buffer.getvalue())),
                "problems": self.problems
            }
        }, upsert=True)

    def can_run(self):
        return self.object.is_managed

    @contextlib.contextmanager
    def check_timer(self, name):
        t = time.time()
        yield
        self.check_timings += [(name, time.time() - t)]

    def set_problem(self, name, problem):
        self.problems[name] = problem


class DiscoveryCheck(object):
    name = None
    # If not none, check required script is available
    # before running check
    required_script = None
    # If not none, check object has all required capablities
    # from list
    required_capabilities = None

    def __init__(self, job):
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

    def has_required_script(self):
        return (not self.required_script or
                self.required_script in self.object.scripts)

    def has_required_capabilities(self):
        if not self.required_capabilities:
            return True
        caps = self.object.get_caps()
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
        with self.job.check_timer(self.name):
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
            except RPCError as e:
                self.set_problem("RPC Error: %s" % e)
                self.logger.error("Terminated due RPC error: %s", e)
            except Exception:
                self.set_problem("Unhandled exception")
                error_report(logger=self.logger)

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
        for k, v in values.items():
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
        name = mo.profile.convert_interface_name(name)
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

    def set_problem(self, problem):
        self.job.set_problem(self.name, problem)


class TopologyDiscoveryCheck(DiscoveryCheck):
    def __init__(self, *args, **kwargs):
        super(TopologyDiscoveryCheck, self).__init__(*args, **kwargs)
        self.neighbor_hostname_cache = {}  # (method, id) -> managed object
        self.neighbor_ip_cache = {}  # (method, ip) -> managed object
        self.neighbor_mac_cache = {}  # (method, mac) -> managed object
        self.neighbor_id_cache = {}

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
            confirmed = set()
            for li, ro_id, ri in self.iter_neighbors(remote_object):
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
                self.reject_link(
                    self.object, l,
                    remote_object, r
                )
            for l, r in candidates[remote_object] & confirmed:
                self.confirm_link(
                    self.object, l,
                    remote_object, r
                )
        if problems:
            self.set_problem(problems)

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
        """
        return remote_object.profile.convert_interface_name(
            remote_interface
        )

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
        if li.type == "aggregated" and ri.type != "aggregated":
            self.logger.error(
                "Cannot connect aggregated interface %s:%s to non-aggregated %s:%s",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        if ri.type == "aggregated" and li.type != "aggregated":
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
