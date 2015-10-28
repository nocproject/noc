# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
# from noc.lib.validators import is_int, is_ipv4
import re


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<chassis_id>\S+)\s+"
        r"(?P<port_id>\S+)\s+(?P<system_name>\S+)\s+"
        r"(?P<caps>.+?)\s+\d+", re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        # For each interface
        for match in self.rx_line.finditer(v):
            i = {"local_interface": match.group("interface"), "neighbors": []}
            # Get capabilities
            cap = 0
            for c in match.group("caps").split(","):
                c = c.strip()
                if c:
                    cap |= {
                        "O": 1, "P": 2, "B": 4,
                        "W": 8, "R": 16, "T": 32,
                        "C": 64, "S": 128
                    }[c]
            neighbor = {
                "remote_chassis_id": match.group("chassis_id"),
                "remote_port": match.group("port_id"),
                "remote_system_name": match.group("system_name"),
                "remote_capabilities": cap
            }
            i["neighbors"] += [neighbor]
            r += [i]
        return r
