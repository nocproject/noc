## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Link Discovery Abstract Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
from collections import defaultdict
## NOC modules
from base import MODiscoveryJob
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.inv.models.link import Link


class LinkDiscoveryJob(MODiscoveryJob):
    """
    Abstract class for link discovery jobs
    """
    name = None
    map_task = None
    method = None
#    ignored = not config.getboolean("interface_discovery", "enabled")
#    initial_submit_interval = config.getint("interface_discovery",
#        "initial_submit_interval")
#    initial_submit_concurrency = config.getint("interface_discovery",
#        "initial_submit_concurrency")
    strict_pending_candidates_check = True

    def is_submitted(self, local_interface, remote_object,
                     remote_interface):
        return (local_interface, remote_object, remote_interface) in self.submited

    def get_interface_by_name(self, object, name):
        """
        Find interface by name
        :param object: Managed Object
        :param name: interface name
        :return: Interface instance or None
        """
        i = Interface.objects.filter(
            managed_object=object.id, name=name).first()
        if i:
            return i
        # Construct alternative names
        alt_names = object.profile.get_interface_names(name)
        nn = object.profile.convert_interface_name(name)
        if nn != name:
            alt_names = [nn] + alt_names
        for n in alt_names:
            i = Interface.objects.filter(
                managed_object=object.id, name=n).first()
            if i:
                return i
        return None

    def submit_candidate(self, local_interface,
                         remote_object, remote_interface=None):
        """
        Submit link candidate
        :param local_interface:
        :param remote_object:
        :param remote_interface:
        :return:
        """
        if (remote_interface and
            self.is_submitted(local_interface, remote_object,
                remote_interface)):
            return  # Already submitted as link
        if (remote_object in self.candidates and
            (local_interface, remote_interface) in self.candidates[remote_object]):
            return  # Already submitted as candidate
        i = self.get_interface_by_name(self.object, local_interface)
        if i:
            if i.is_linked:
                return  # Already linked
        else:
            return  # Interface not found
        self.debug("Link candidate found: %s -> %s:%s" % (
            local_interface, remote_object.name, remote_interface))
        self.candidates[remote_object] += [
            (local_interface, remote_interface)
        ]

    def submit_link(self, local_object, local_interface,
                    remote_object, remote_interface):
        l_iface = self.get_interface_by_name(local_object, local_interface)
        if not l_iface:
            self.error("Interface is not found: %s:%s" % (
                local_object.name, local_interface))
            return
        r_iface = self.get_interface_by_name(remote_object, remote_interface)
        if not r_iface:
            self.error("Interface is not found: %s:%s" % (
                remote_object.name, remote_interface))
            return
        self.info("Linking %s and %s" % (l_iface, r_iface))
        try:
            l_iface.link_ptp(r_iface, method=self.method)
        except ValueError, why:
            self.error("Linking error: %s" % why)
        self.submited.add((local_interface, remote_object, remote_interface))

    def process_result(self, object, result):
        """
        Process job result and submit candidates
        :param result:
        :return:
        """
        pass

    def load_existing_links(self, object):
        for l in Link.object_links(object):
            if l.is_ptp:
                i1, i2 = l.interfaces
                if l.is_loop:
                    # Loop to self
                    self.submited.add((i1.name, object, i2.name))
                    self.submited.add((i2.name, object, i1.name))
                else:
                    # p2p link
                    if i1.managed_object == object:
                        self.submited.add((i1.name, i2.managed_object, i2.name))
                    else:
                        self.submited.add((i2.name, i1.managed_object, i1.name))

    def load_pending_checks(self, object):
        for plc in PendingLinkCheck.objects.filter(
            method=self.method, local_object=object.id,
            expire__gt=datetime.datetime.now()):
            if (self.strict_pending_candidates_check and
                plc.remote_object not in self.candidates):
                continue  # Ignore uncheckable links
            local_interface = plc.local_interface
            remote_interface = plc.remote_interface
            if local_interface is None and remote_interface is None:
                continue  # Failed to map
            if (remote_interface and
                self.is_submitted(local_interface,
                    plc.remote_object, remote_interface)):
                # Already submitted link
                continue
            if (plc.remote_object in self.p_candidates and
                (local_interface, remote_interface) in self.p_candidates[plc.remote_object]):
                # Suppress duplicates
                continue
            self.debug("Pending link check: %s:%s -> %s:%s" % (
                object.name, local_interface,
                plc.remote_object.name, remote_interface))
            self.p_candidates[plc.remote_object] += [
                (local_interface, remote_interface)]

    def reschedule_pending_jobs(self, object):
        so = set([object]) | set(o for (l, o, r) in self.submited)
        for o in set(self.candidates) - set(self.p_candidates) - so:
            self.run_on_complete(self.name, o.id)

    def clean_pending_checks(self, object):
        PendingLinkCheck.objects.filter(
            method=self.method, local_object=object.id).delete()

    def write_pending_checks(self, object):
        for o in self.candidates:
            for l, r in self.candidates[o]:
                if not self.is_submitted(l, o, r):
                    i = self.get_interface_by_name(object, l)
                    if i and not i.is_linked:
                        self.debug("Scheduling check for %s:%s -> %s:%s" % (
                            object.name, l, o, r))
                        PendingLinkCheck.submit(self.method, o, r, object, l)

    def process_pending_checks(self, object):
        for pr in self.p_candidates:
            # Check remote object in pending checks
            if pr not in self.candidates:
                continue
            pc = self.p_candidates[pr]
            c = self.candidates[pr]
            if len(pc) == 1 and len(c) == 1:
                # single link
                pcl, pcr = pc[0]
                cl, cr = c[0]
                if ((pcl is None or cl is None or pcl == cl) and
                    (pcr is None or cr is None or pcr == cr)):
                    self.submit_link(object, cl, pr, pcr)
            else:
                # multilink
                # Find full match
                for l, r in pc:
                    if (l, r) in c:
                        self.submit_link(object, l, pr, r)

    def resolve_self_links(self, object):
        if object in self.candidates:
            sl = set()
            for l, r in self.candidates[object]:
                if (l and r and l != r and (l, r) not in sl
                    and (r, l) not in sl):
                    sl.add((l, r))
            for l, r in sl:
                self.submit_link(object, l, object, r)

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        # Caches
        self.neighbor_by_mac_cache = {}  # mac -> object
        self.own_mac_cache = {}  # mac -> true | false
        self.own_macs = None  # [(first_mac, last_mac), ...]
        # Fetch existing links
        self.submited = set()  # (local_iface, remote_object, remote_iface)
        self.load_existing_links(object)
        # Process results
        self.candidates = defaultdict(list)  # remote -> [(local iface, remote_iface)]
                                             # remote iface may be unknown
        self.process_result(object, result)
        # Fetch pending link checks
        self.p_candidates = defaultdict(list)  # remote -> [(local iface, remote_iface)]
                                               # local iface may be unknown
        self.load_pending_checks(object)
        # Resolve self links
        self.resolve_self_links(object)
        # Process pending checks
        self.process_pending_checks(object)
        # Clean my pending link checks
        self.clean_pending_checks(object)
        # Write pending checks
        self.write_pending_checks(object)
        # Reschedule pending jobs
        self.reschedule_pending_jobs(object)
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_%s_discovery" % cls.method: True}

    def can_run(self):
        return (super(LinkDiscoveryJob, self).can_run()
                and getattr(self.object.object_profile,
                    "enable_%s_discovery" % self.method))

    @classmethod
    def get_submit_interval(cls, object):
        return getattr(object.object_profile,
            "%s_discovery_max_interval" % cls.method)

    def get_failed_interval(self):
        return getattr(self.object.object_profile,
            "%s_discovery_min_interval" % self.method)

    def get_neighbor_by_mac(self, mac):
        """
        Find neighbor by MAC address
        :param mac:
        :return:
        """
        # Use cached values
        o = self.neighbor_by_mac_cache.get(mac)
        if not o:
            # Find in discovery cache
            o = DiscoveryID.find_object(mac=mac)
            if not o:
                # Fallback to interface's MAC
                mos = set(i.managed_object
                          for i in Interface.objects.filter(mac=mac))
                if len(mos) == 1:
                    o = mos.pop()
            self.neighbor_by_mac_cache[mac] = o
        return o

    def is_own_mac(self, mac):
        """
        Check the MAC belongs to object
        :param mac:
        :return:
        """
        if self.own_macs is None:
            r = DiscoveryID.macs_for_object(self.object)
            if not r:
                self.own_macs = []
                return False
        if self.own_macs:
            mr = self.own_mac_cache.get(mac)
            if mr is None:
                mr = False
                for f, t in self.own_macs:
                    if f <= mac <= t:
                        mr = True
                        break
                self.own_mac_cache[mac] = mr
            return mr
        else:
            return False
