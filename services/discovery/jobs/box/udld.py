# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UDLD check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.inv.models.discoveryid import DiscoveryID
# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class UDLDCheck(TopologyDiscoveryCheck):
    """
    UDLD Topology discovery
    """
    name = "udld"
    required_script = "get_udld_neighbors"
    required_capabilities = ["Network | UDLD"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_udld_neighbors()
        for n in result["neighbors"]:
            yield (
                n["local_interface"],
                n["remote_device"],
                n["remote_interface"]
            )

    def get_neighbor(self, device_id):
        return DiscoveryID.get_by_udld_id(device_id)
