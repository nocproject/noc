# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei NDP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class HuaweiNDPCheck(TopologyDiscoveryCheck):
    """
    CDP Topology discovery
    """
    name = "huawei_ndp"
    required_script = "get_huawei_ndp_neighbors"
    required_capabilities = ["Huawei | NDP"]

    def iter_neighbors(self, mo):
        for n in mo.scripts.get_huawei_ndp_neighbors():
            if len(n["neighbors"]) == 1:
                nn = n["neighbors"][0]
                yield (
                    n["local_interface"],
                    nn["chassis_mac"],
                    nn["interface"]
                )

    def get_neighbor(self, n):
        return self.get_neighbor_by_mac(n)
