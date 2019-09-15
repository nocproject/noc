# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.base import IPv4Parameter
from noc.core.text import parse_table


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_entity = re.compile(
        r"^\s+Chassis ID Subtype\s+:(?P<chassis_id_type>.+)\s*\n"
        r"^\s+Chassis ID\s+:(?P<chassis_id>.+)\s*\n"
        r"^\s+Port ID Subtype\s+:(?P<port_id_type>.+)\s*\n"
        r"^\s+Port ID\s+:(?P<port_id>.+)\s*\n"
        r"^\s+Port Description\s+:(?P<port_description>(.|\n)*)\n"
        r"^\s+System Name\s+:(?P<system_name>.*)\n"
        r"^\s+System Description\s+:(?P<system_description>(.|\n)*)\n"
        r"^\s+System Capabilities\s+:(?P<system_capabilities>.*)\n",
        re.MULTILINE,
    )

    def execute(self):
        r = []
        v = self.cli("show interfaces status")
        t = parse_table(v)
        for i in t:
            iface = {"local_interface": i[0], "neighbors": []}
            v = self.cli("show lldp neighbors interface %s" % i[0])
            for m in self.rx_entity.finditer(v):
                n = {}
                n["remote_chassis_id_subtype"] = {
                    "chassis component": 1,
                    "interface alias": 2,
                    "port component": 3,
                    "mac address": 4,
                    "network address": 5,
                    "interface name": 6,
                    "local": 7,
                }[m.group("chassis_id_type").strip().lower()]
                n["remote_chassis_id"] = m.group("chassis_id").strip()
                remote_port_subtype = m.group("port_id_type")
                remote_port_subtype.replace("_", " ")
                n["remote_port_subtype"] = {
                    "interface alias": 1,
                    "port component": 2,
                    "mac address": 3,
                    "network address": 4,
                    "interface name": 5,
                    "agent circuit id": 6,
                    "local": 7,
                }[remote_port_subtype.strip().lower()]
                n["remote_port"] = m.group("port_id").strip()
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
                if n["remote_port_subtype"] == 4:
                    n["remote_port"] = IPv4Parameter().clean(n["remote_port"])

                if m.group("port_description").strip():
                    n["remote_port_description"] = re.sub(
                        r"\n\s*", "", m.group("port_description").strip()
                    )
                if m.group("system_name").strip():
                    n["remote_system_name"] = m.group("system_name").strip()
                if m.group("system_description").strip():
                    n["remote_system_description"] = re.sub(
                        r"\n\s*", "", m.group("system_description").strip()
                    )
                caps = 0
                for c in m.group("system_capabilities").split(","):
                    c = c.strip()
                    if not c:
                        break
                    caps |= {
                        "Other": 1,
                        "Repeater": 2,
                        "Bridge": 4,
                        "WLAN Access Point": 8,
                        "Router": 16,
                        "Telephone": 32,
                        "DOCSIS Cable Device": 64,
                        "Station Only": 128,
                    }[c]
                n["remote_capabilities"] = caps
                iface["neighbors"] += [n]
            if iface["neighbors"]:
                r += [iface]
        return r
