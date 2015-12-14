# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CDP check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.inv.models.discoveryid import DiscoveryID


class CDPCheck(TopologyDiscoveryCheck):
    """
    CDP Topology discovery
    """
    name = "cdp"
    required_script = "get_cdp_neighbors"
    required_capabilities = ["Network | CDP"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_cdp_neighbors()
        for n in result["neighbors"]:
            yield (
                n["local_interface"],
                n["device_id"],
                n["remote_interface"]
            )

    get_neighbor = TopologyDiscoveryCheck.get_neighbor_by_hostname
