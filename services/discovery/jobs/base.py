#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic MO discovery job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.lib.debug import error_report
from noc.lib.log import PrefixLoggerAdapter
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.interfaces.base import MACAddressParameter, InterfaceTypeError


class MODiscoveryJob(PeriodicJob):
    model = ManagedObject
    use_offset = True

    def can_run(self):
        return self.object.is_managed


class DiscoveryCheck(object):
    name = None
    # If not none, check required script is available
    # before running check
    required_script = None

    def __init__(self, job):
        self.job = job
        self.object = self.job.object
        self.logger = PrefixLoggerAdapter(
            self.job.logger.logger,
            "%s][%s][%s" % (self.job.name, self.name, self.object.name)
        )
        self.if_name_cache = {}  # mo, name -> Interface
        self.if_mac_cache = {}  # mo, mac -> Interface
        self.if_ip_cache = {}
        self.sub_cache = {}
        self.profile_cache = {}

    def run(self):
        if (self.required_script and
                self.required_script not in self.object.scripts):
            self.logger.info("%s script is not supported. Skipping",
                             self.required_script)
            return
        try:
            self.handler()
        except Exception:
            error_report()

    def handler(self):
        pass

    def update_if_changed(self, obj, values, ignore_empty=None):
        """
        Update fields if changed.
        :param obj: Document instance
        :type obj: Document
        :param values: New values
        :type values: dict
        :param ignore_empty: List of fields which may be ignored if empty
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
            obj.save()
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
        key = (mo, name)
        if key not in self.if_name_cache:
            i = Interface.objects.filter(
                managed_object=self.object.id,
                name=name
            ).first()
            self.if_name_cache[key] = i
        return self.if_name_cache[key]

    def get_interface_by_mac(self, mac, mo=None):
        """
        Returns Interface instance referred by MAC address
        """
        mo = mo or self.object
        key = (mo, mac)
        if key not in self.if_mac_cache:
            li = list(Interface.objects.filter(
                managed_object=self.object.id,
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
        self.if_name_cache[name] = iface

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


class TopologyDiscoveryCheck(DiscoveryCheck):
    def __init__(self, *args, **kwargs):
        super(TopologyDiscoveryCheck, self).__init__(*args, **kwargs)
        self.neighbor_hostname_cache = {}  # (method, id) -> managed object
        self.neighbor_ip_cache = {}  # (method, ip) -> managed object
        self.neighbor_mac_cache = {}  # (method, mac) -> managed object

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        # remote object -> [(local, remote), ..]
        candidates = defaultdict(set)
        loops = {}  # first interface, second interface
        for li, ro, ri in self.iter_neighbors(self.object):
            # Resolve remote object
            remote_object = self.get_neighbor(ri)
            if not remote_object:
                self.logger.debug(
                    "Remote object '%s' is not found. Skipping",
                    ri
                )
                continue
            # Resolve remote interface name
            remote_interface = self.get_remote_interface(
                remote_object,
                ri
            )
            # Detecting loops
            if remote_object.id == self.object.id:
                loops[li] = remote_interface
                if (remote_interface in loops and loops[remote_interface] == li):
                    self.logger.debug(
                        "Loop link detected: %s:%s - %s:%s",
                        self.object.name, li,
                        self.object.name, remote_interface)
                    self.confirm_link(
                        self.object, li,
                        remote_object, remote_interface
                    )
                continue
            # Submitting candidates
            self.logger.debug(
                "Link candidate: %s:%s - %s:%s",
                self.object.name, li,
                remote_object.name, remote_interface
            )
            candidates[remote_object].add((li, remote_interface))

        # Checking candidates from remote side
        for remote_object in candidates:
            if (self.required_script and
                    self.required_script not in remote_object.scripts):
                self.logger.debug(
                    "Remote object '%s' does not support %s script. "
                    "Cannot confirm links",
                    remote_object.name
                )
            confirmed = set()
            for li, ro_id, ri in self.iter_neighbors(remote_object):
                ro = self.get_neighbor(ro_id)
                if not ro or ro.id != self.object.id:
                    continue  # To other objects
                remote_interface = self.get_remote_interface(
                    self.object,
                    ri
                )
                confirmed.add((remote_interface, li))
            for l, r in candidates[remote_object] & confirmed:
                self.confirm_link(
                    self.object, l,
                    remote_object, r
                )
            for l, r in candidates[remote_object] - confirmed:
                self.reject_link(
                    self.object, l,
                    remote_object, r
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
        return self.neighbor_hostname_cache[hostname]

    get_neighbor = get_neighbor_by_hostname

    def get_neighbor_by_mac(self, mac):
        """
        Resolve neighbor by hostname
        """
        if mac not in self.neighbor_mac_cache:
            d = DiscoveryID.find_object(mac)
            self.neighbor_mac_cache[mac] = d
        return self.neighbor_mac_cache[mac]

    def get_neighbor_by_ip(self, ip):
        """
        Resolve neighbor by hostname
        """
        if ip not in self.neighbor_ip_cache:
            d = DiscoveryID.objects.filter(router_id=ip).first()
            if d:
                self.neighbor_ip_cache[ip] = d.object
            else:
                # @todo: Try interface lookup
                self.neighbor_ip_cache[ip] = None
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
        # Get interfaces
        li = self.get_interface_by_name(mo=local_object,
                                        name=local_interface)
        if not li:
            self.logger.debug(
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
            self.logger.debug(
                "Not linking: %s:%s -- %s:%s. "
                "Interface %s is not discovered",
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
            self.logger.debug(
                "Already linked: %s:%s -- %s:%s",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            llink.touch(self.name)
            return
        # Check method preferences
        if llink and not self.is_preferable_over(llink.discovery_method):
            self.logger.debug(
                "Not linking: %s:%s -- %s:%s. "
                "'%s' method is preferable over '%s'",
                local_object.name, local_interface,
                remote_object.name, remote_interface,
                llink.discovery_method, self.name
            )
            return
        if rlink and not self.is_preferable_over(rlink.discovery_method):
            self.logger.debug(
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
        lpolicy = llink.interface_profile.discovery_policy
        rpolicy = llink.interface_profile.discovery_policy
        #
        if lpolicy == "I" or rpolicy == "I":
            self.logger.debug(
                "Not linking: %s:%s -- %s:%s. "
                "'Ignore' interface discovery policy set",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        #
        if (lpolicy == "O" and llink) or (lpolicy == "O" and llink):
            self.logger.debug(
                "Not linking: %s:%s -- %s:%s. "
                "'Create new' interface discovery policy set and "
                "interface is already linked",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        #
        if lpolicy in ("O", "R") and rpolicy in ("O", "R"):
            self.logger.debug(
                "Linking: %s:%s -- %s:%s",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            li.link_ptp(ri, method=self.name)
            return
        #
        if lpolicy == "C" and rpolicy == "C":
            self.logger.debug(
                "Not linking: %s:%s -- %s:%s. "
                "Cloud merging is forbidden",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            return
        #
        if lpolicy == "C":
            if rlink:
                if rpolicy == "O":
                    self.logger.debug(
                        "Not linking: %s:%s -- %s:%s. "
                        "Already linked. "
                        "Connecting to cloud is forbidden by policy",
                        local_object.name, local_interface,
                        remote_object.name, remote_interface
                    )
                    return
                else:
                    ri.unlink()
            if llink:
                # Attach to existing cloud
                llink.interfaces = llink.interfaces + [ri]
                llink.save()
            else:
                # Create p2p link
                li.link_ptp(ri, method=self.name)
        if rpolicy == "C":
            if llink:
                if lpolicy == "O":
                    self.logger.debug(
                        "Not linking: %s:%s -- %s:%s. "
                        "Already linked. "
                        "Connecting to cloud is forbidden by policy",
                        local_object.name, local_interface,
                        remote_object.name, remote_interface
                    )
                    return
                else:
                    li.unlink()
            if rlink:
                # Attach to existing cloud
                rlink.interfaces = rlink.interfaces + [li]
                rlink.save()
            else:
                # Create p2p link
                ri.link_ptp(li, method=self.name)
        #
        self.logger.debug(
            "Not linking: %s:%s -- %s:%s. "
            "Link creating not allowed",
            local_object.name, local_interface,
            remote_object.name, remote_interface
        )

    def reject_link(self, local_object, local_interface,
                    remote_object, remote_interface):
                # Get interfaces
        li = self.get_interface_by_name(mo=local_object,
                                        name=local_interface)
        if not li:
            self.logger.debug(
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
            self.logger.debug(
                "Cannot unlink: %s:%s -- %s:%s. "
                "Interface %s is not discovered",
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
            self.logger.debug(
                "Unlinking: %s:%s -- %s:%s. ",
                local_object.name, local_interface,
                remote_object.name, remote_interface
            )
            llink.delete()
        else:
            self.logger.debug(
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
