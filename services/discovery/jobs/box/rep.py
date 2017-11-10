# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# REP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.inv.models.discoveryid import DiscoveryID


class REPCheck(TopologyDiscoveryCheck):
    """
    REP Topology discovery
    """
    name = "rep"
    required_script = "get_rep_neighbors"
    required_capabilities = ["Network | REP"]
    own_mac_cache = {}
    own_macs = None  # [(first_mac, last_mac), ...]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_rep_neighbors()
        for segment in result:
            topology = segment["topology"]
            # Find own ports
            o = [i for i, p in enumerate(topology)
                 if self.is_own_mac(p["mac"])]
            if not o:
                continue  # Not found
            elif len(o) != 2:
                # Something strange
                self.logger.error("Invalid REP discovery result: %r" % topology)
                continue
            elif len(o) == 2:
                f, s = o
                remote_info, local_info = None, None
                L = len(topology)
                if not topology[f]["edge_no_neighbor"]:
                    remote_info, local_info = topology[f], topology[(f - 1) % L]
                if not topology[s]["edge_no_neighbor"]:
                    remote_info, local_info = topology[s], topology[(s + 1) % L]

                if remote_info and local_info:
                    remote_object = self.get_neighbor_by_mac(remote_info["mac"])
                    if not remote_object:
                        continue
                    yield (
                        local_info,
                        remote_object,
                        remote_info
                    )

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
