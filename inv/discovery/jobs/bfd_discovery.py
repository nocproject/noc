## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BFD Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config
from noc.inv.models.subinterface import SubInterface


class BFDLinkDiscoveryJob(LinkDiscoveryJob):
    """
    BFD protocol link discovery
    """
    name = "bfd_discovery"
    map_task = "get_bfd_sessions"
    method = "bfd"
    ignored = not config.getboolean("bfd_discovery", "enabled")
    strict_pending_candidates_check = False

    def process_result(self, object, result):
        self.ld = {}  # local discriminator -> port name
        self.n_cache = {}  # address -> neighbor
        for session in result:
            if "L2" not in session["clients"]:
                continue
            self.ld[session["local_discriminator"]] = session["local_interface"]
            remote_object = self.get_neighbor(session["remote_address"])
            if not remote_object:
                continue
            self.submit_candidate(session["local_interface"],
                remote_object,
                str(session["remote_discriminator"])
            )
        self.debug("Candidates: %s" % self.candidates)

    def process_pending_checks(self, object):
        self.debug("Process pending checks: %s" % self.p_candidates)
        for remote_object in self.p_candidates:
            for disc, remote_interface in self.p_candidates[remote_object]:
                disc = int(disc)
                local_interface = self.ld.get(disc)
                if local_interface:
                    self.submit_link(
                        object, local_interface,
                        remote_object, remote_interface)
                    self.submited.add((str(disc), remote_object, remote_interface))
                else:
                    self.debug("Local discriminator %d is not found in %s" % (
                        disc, ", ".join(str(k) for k in self.ld)))

    def get_neighbor(self, address):
        """
        Find neighbor by ip interface
        :param address:
        :return:
        """
        # Get cached
        n = self.n_cache.get(address)
        if n:
            return n
        # @todo: Optimize search
        subs = list(SubInterface.objects.filter(
            enabled_afi="IPv4",
            ipv4_addresses__startswith="%s/" % address))
        if len(subs) == 1:
            # Exact match
            n = subs[0].managed_object
        else:
            n = None
        self.n_cache[address] = n
        return n
