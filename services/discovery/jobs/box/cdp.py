# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CDP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.lib.validators import is_ipv4, is_mac


class CDPCheck(TopologyDiscoveryCheck):
    """
    CDP Topology discovery
    """
    name = "cdp"
    required_script = "get_cdp_neighbors"
    required_capabilities = ["Network | CDP"]

    RESERVED_NAMES = set(["Switch", "Router", "MikroTik"])

    def iter_neighbors(self, mo):
        result = mo.scripts.get_cdp_neighbors()
        for n in result["neighbors"]:
            device_id = n["device_id"]
            if device_id in self.RESERVED_NAMES and n.get("remote_ip"):
                device_id = n["remote_ip"]
            yield (
                n["local_interface"],
                device_id,
                n["remote_interface"]
            )

    def get_neighbor(self, n):
        nn = self.get_neighbor_by_hostname(n)
        if nn:
            return nn
        if is_ipv4(n):
            return self.get_neighbor_by_ip(n)
        elif is_mac(n):
            return self.get_neighbor_by_mac(n)
        else:
            return None
