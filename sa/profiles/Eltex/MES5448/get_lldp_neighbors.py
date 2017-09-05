# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4, is_ipv6, is_mac
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^Chassis ID Subtype: (?P<chassis_id_subtype>.+?)\n"
        r"^Chassis ID: (?P<chassis_id>.+?)\n"
        r"^Port ID Subtype: (?P<port_id_subtype>.+?)\n"
        r"^Port ID: (?P<port_id>.+?)\n"
        r"^System Name:(?P<system_name>.*?)\n"
        r"^System Description:(?P<system_description>.*?)\n"
        r"^Port Description:(?P<port_description>.*?)\n"
        r"^System Capabilities Supported:.*?\n"
        r"^System Capabilities Enabled:(?P<caps>.*?)\n",
        re.MULTILINE | re.DOTALL
    )
    CAPS_MAP = {
        "repeater": 2,
        "bridge": 4,
        "WLAN access point": 8,
        "router": 16
    }
    CHASSIS_SUBTYPE = {
        "MAC Address": 4
    }
    PORT_SUBTYPE = {
        "Interface Alias": 1,
        "MAC Address": 3,
        "Interface Name": 5,
        "Local": 7
    }

    def execute(self):
        r = []
        for i in parse_table(self.cli("show lldp remote-device all")):
            if not i[1]:
                continue
            c = self.cli("show lldp remote-device detail %s" % i[0])
            iface = {
                "local_interface": i[0],
                "neighbors": []
            }
            for match in self.rx_detail.finditer(c):
                cap = 0
                for c in match.group("caps").split(","):
                    c = c.strip()
                    if c:
                        cap |= self.CAPS_MAP[c]
                n = {
                    "remote_chassis_id": match.group("chassis_id").strip(),
                    "remote_chassis_id_subtype": self.CHASSIS_SUBTYPE[
                        match.group("chassis_id_subtype").strip()
                    ],
                    "remote_port":  match.group("port_id").strip(),
                    "remote_port_subtype": self.PORT_SUBTYPE[
                        match.group("port_id_subtype").strip()
                    ],
                    "remote_capabilities": cap,
                }
                if match.group("system_name").strip():
                    n["remote_system_name"] = match.group("system_name").strip()
                if match.group("system_description").strip():
                    n["remote_system_description"] = \
                    match.group("system_description").strip()
                if match.group("port_description").strip():
                    n["remote_port_description"] = \
                        match.group("port_description").strip()
                iface["neighbors"] += [n]
            r += [iface]
        return r
