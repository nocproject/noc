# ---------------------------------------------------------------------
# FDP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class FDPCheck(TopologyDiscoveryCheck):
    """
    FDP Topology discovery (Foundry Discovery Protocol)
    """

    name = "fdp"
    required_script = "get_fdp_neighbors"
    required_capabilities = ["Network | FDP"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_fdp_neighbors()
        for n in result["neighbors"]:
            device_id = n["device_id"]
            yield (n["local_interface"], device_id, n["remote_interface"])

    def get_neighbor(self, n):
        # @todo get_neighbors_by_serial
        nn = self.get_neighbor_by_hostname(n)
        if nn:
            return nn
        return None
