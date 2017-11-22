# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# REP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class REPCheck(TopologyDiscoveryCheck):
    """
    REP Topology discovery
    """
    name = "rep"
    required_script = "get_rep_neighbors"
    required_capabilities = ["Cisco | REP"]

    def iter_neighbors(self, mo):
        self.own_macs = None
        result = mo.scripts.get_rep_neighbors()
        for segment in result:
            topology = segment["topology"]
            # Find own ports
            o = [i for i, p in enumerate(topology)
                 if self.is_own_mac(p["mac"])]
            if not o:
                continue  # Not found
            elif len(o) != 2:
                # Something strange. REP Topology is ring, more 2 neighbors is strange...
                self.logger.error("Invalid REP discovery result: %r" % topology)
                continue
            elif len(o) == 2:
                # Left and right ports
                f, s = o
                remote_info, local_info = None, None
                # Length rings
                L = len(topology)
                if not topology[f]["edge_no_neighbor"]:
                    # Right
                    remote_info, local_info = topology[f], topology[(f - 1) % L]
                if not topology[s]["edge_no_neighbor"]:
                    # Left
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
