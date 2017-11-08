# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.base import IPv4Parameter
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "DLink.DxS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_port = re.compile(
        r"^Port ID : (?P<port>\S+)\s*\n"
        r"^-+\s*\n"
        r"^Remote Entities Count : [1-9]+\s*\n"
        r"(?P<entities>.+?): \d+\s*\n\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_entity = re.compile(
        r"^Entity \d+\s*\n"
        r"^\s+Chassis ID Subtype\s+:(?P<chassis_id_subtype>.+)\s*\n"
        r"^\s+Chassis ID\s+:(?P<chassis_id>.+)\s*\n"
        r"^\s+Port ID Subtype\s+:(?P<port_id_subtype>.+)\s*\n"
        r"^\s+Port ID\s+:(?P<port_id>.+)\s*\n"
        r"^\s*Port Description\s+:(?P<port_description>.*)"
        r"^\s+System Name\s+:(?P<system_name>.*)"
        r"^\s+System Description\s+:(?P<system_description>.*)"
        r"^\s+System Capabilities\s+:(?P<system_capabilities>.+?)\s*\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp remote_ports mode normal")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_port.finditer(v):
            i = {
                "local_interface": match.group("port"),
                "neighbors": []
            }
            for m in self.rx_entity.finditer(match.group("entities")):
                n = {}
                n["remote_chassis_id_subtype"] = {
                    "chassis component": 1,
                    "interface alias": 2,
                    "port component": 3,
                    "port_component": 3,
                    "mac address": 4,
                    "macaddress": 4,
                    "network address": 5,
                    "network_address": 5,
                    "interface name": 6,
                    "local": 7
                }[m.group("chassis_id_subtype").strip().lower()]
                n["remote_chassis_id"] = m.group("chassis_id").strip()
                remote_port_subtype = m.group("port_id_subtype")
                remote_port_subtype.replace("_", " ")
                n["remote_port_subtype"] = {
                    "interface alias": 1,
                    # DES-3526 6.00 B48 and DES-3526 6.00 B49
                    "nterface alias": 1,
                    # DES-3200-28 1.85.B008
                    "nterface_alias": 1,
                    "port component": 2,
                    "port_component": 2,
                    "mac address": 3,
                    "macaddress": 3,
                    "network address": 4,
                    "interface name": 5,
                    "interface_name": 5,
                    "agent circuit id": 6,
                    "locally assigned": 7,
                    "local": 7
                }[remote_port_subtype.strip().lower()]
                n["remote_port"] = m.group("port_id").strip()
                if n["remote_port_subtype"] == 3:
                    n["remote_port"] = \
                        MACAddressParameter().clean(n["remote_port"])
                if n["remote_port_subtype"] == 4:
                    n["remote_port"] = \
                        IPv4Parameter().clean(n["remote_port"])

                if m.group("port_description").strip():
                    p = m.group("port_description").strip()
                    n["remote_port_description"] = re.sub("\n\s{49}", "", p)
                if m.group("system_name").strip():
                    p = m.group("system_name").strip()
                    n["remote_system_name"] = re.sub("\n\s{49}", "", p)
                if m.group("system_description").strip():
                    p = m.group("system_description").strip()
                    n["remote_system_description"] = re.sub("\n\s{49}", "", p)
                caps = 0
                for c in m.group("system_capabilities").split(","):
                    c = c.strip()
                    if not c:
                        break
                    caps |= {
                        "Other": 1,
                        "Repeater": 2,
                        "Bridge": 4,
                        "Access Point": 8,
                        "WLAN Access Point": 8,
                        "Router": 16,
                        "Telephone": 32,
                        "DOCSIS Cable Device": 64,
                        "Station Only": 128
                    }[c]
                n["remote_capabilities"] = caps
                i["neighbors"] += [n]
            if i["neighbors"]:
                r += [i]
        return r
