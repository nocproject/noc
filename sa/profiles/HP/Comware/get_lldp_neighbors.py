# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "HP.Comware.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_item = re.compile(
        r"^LLDP neighbor-information of port \d+\[(?P<interface>\S+)\]\:\n"
        r"^  Neighbor index   : \d+\n"
        r"^  Update time      : .+?\n"
        r"^  Chassis type     : (?P<chassis_type>.+?)\n"
        r"^  Chassis ID       : (?P<chassis_id>\S+)\n"
        r"^  Port ID type     : (?P<port_id_type>.+?)\n"
        r"^  Port ID          : (?P<port_id>.+?)\n"
        r"^  Port description : (?P<port_descr>.+?)\n"
        r"^  System name        : (?P<system_name>.+?)\n"
        r"(^  System description : (?P<system_descr>.+?)\n)?"
        r"(^  System capabilities supported : (?P<system_caps_s>.+?)\n)?",
        re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("display lldp neighbor-information")
        except self.CLISyntaxError:
            return []
        for match in self.rx_item.finditer(v):
            i = {"local_interface": match.group("interface"), "neighbors": []}
            n = {}
            n["remote_chassis_id_subtype"] = {
                "Chassis Component": 1,
                "Interface Alias": 2,
                "Port Component": 3,
                "MAC Address": 4,
                "Network Address": 5,
                "Interface Name": 6,
                "local": 7
            }.get(match.group("chassis_type"))
            n["remote_chassis_id"] = match.group("chassis_id").strip()
            n["remote_port_subtype"] = {
                "Interface Alias": 1,
                "Port Component": 2,
                "MAC Address": 3,
                "Network Address": 4,
                "Interface Name": 5,
                "Agent Circuit ID": 6,
                "Locally assigned": 7
            }.get(match.group("port_id_type"))
            n["remote_port"] = match.group("port_id").strip()
            n["remote_port_description"] = match.group("port_descr").strip()
            n["remote_system_name"] = match.group("system_name").strip()
            if match.group("system_descr"):
                n["remote_system_description"] = match.group("system_descr").strip()
            if match.group("system_caps_s"):
                cap = 0
                for c in match.group("system_caps_s").split(","):
                    c = c.strip()
                    if c:
                        cap |= {
                            "Other": 1, "Repeater": 2, "Bridge": 4,
                            "WLAN Access Point": 8, "Router": 16, "TTelephone": 32,
                            "DOCSIS Cable Device": 64, "Station Only": 128
                        }[c]
                n["remote_capabilities"] = cap
            i["neighbors"] += [n]
            r += [i]
        return r
