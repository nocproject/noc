# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_ipv6_neighbor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetipv6neighbor import IGetIPv6Neighbor


class Script(BaseScript):
    name = "Eltex.ESR.get_ipv6_neighbor"
    interface = IGetIPv6Neighbor

    # Need more exaples
    s_map = {
        "--": "incomplete",
        "REACH": "reachable",
        "stale": "stale",
        "noarp": "delay",
        "PROBE": "probe"
    }

    def execute(self, vrf=None):
        r = []
        c = self.cli("show ipv6 neighbors", cached=True)
        for ifname, ip, mac, state, age in parse_table(c):
            if "." in ifname:
                ifname, vlan_id = ifname.split(".")
            found = False
            for i in r:
                if (ifname == i["interface"]) and (ip == i["ip"]):
                    found = True
                    break
            if found:
                continue
            if mac == "--":
                r += [{
                    "ip": ip,
                    "interface": ifname,
                    "state": self.s_map[state]
                }]
            else:
                r += [{
                    "ip": ip,
                    "mac": mac,
                    "interface": ifname,
                    "state": self.s_map[state]
                }]
        return r
