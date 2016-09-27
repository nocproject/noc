# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_ipv6_neighbor
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetipv6neighbor import IGetIPv6Neighbor


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_ipv6_neighbor"
    interface = IGetIPv6Neighbor

    s_map = {
        "noarp": "incomplete",
        "incomplete": "incomplete",
        "reachable": "reachable",
        "stale": "stale",
        "delay": "delay",
        "probe": "probe"
    }

    def execute(self, vrf=None):
        try:
            v = self.cli_detail("/ipv6 neighbor print detail without-paging")
        except self.CLISyntaxError:
            return []
        nb = []
        for n, f, r in v:
            nb += [{
                "ip": r["address"],
                "mac": r["mac-address"],
                "interface": r["interface"],
                "state": self.s_map[r["status"]]
            }]
        return nb
