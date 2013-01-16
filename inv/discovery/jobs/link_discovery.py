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
from noc.settings import config
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
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
            return  # Already submitted
        if (remote_object in self.candidates and
            (local_interface, remote_interface) in self.candidates[remote_object]):
            return
        self.debug("Link candidate found: %s -> %s:%s" % (
            local_interface, remote_object.name, remote_interface))
        self.candidates[remote_object] += [
            (local_interface, remote_interface)
        ]

    def submit_link(self, local_object, local_interface,
                    remote_object, remote_interface):
        l_iface = Interface.objects.filter(
            managed_object=local_object.id,
            name=local_interface).first()
        if not l_iface:
            self.error("Interface is not found: %s:%s" % (
                local_object.name, local_interface))
            return
        r_iface = Interface.objects.filter(
            managed_object=remote_object.id,
            name=remote_interface).first()
        if not r_iface:
            self.error("Interface is not found: %s:%s" % (
                remote_object.name, remote_interface))
            return
        link = l_iface.link
        self.debug("Linking %s and %s" % (l_iface, r_iface))
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
            self.debug("Rescheduling discovery for: %s" % o.name)
            self.scheduler.reschedule_job(
                self.name, o.id,
                datetime.datetime.now(),  # @todo: Less aggressive
                skip_running=True)

    def clean_pending_checks(self, object):
        PendingLinkCheck.objects.filter(
            method=self.method, local_object=object.id).delete()

    def write_pending_checks(self, object):
        for o in self.candidates:
            for l, r in self.candidates[o]:
                if not self.is_submitted(l, o, r):
                    self.debug("Scheduling check for %s:%s -> %s:%s" % (object.name, l, o, r))
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
        d = DiscoveryID.objects.filter(first_chassis_mac__lte=mac,
            last_chassis_mac__gte=mac).first()
        if d:
            return d.object
        else:
            return None
