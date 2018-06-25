# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.base import IPv4Parameter


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_port = re.compile(
        r"^-+\s*\n"
        r"^Lldp neighbor-information of port \[(?P<port>.+?)\]\s*\n"
        r"^-+\s*\n"
        r"(?P<entities>.+?)\n"
        r"^\s+Maximum frame Size\s+:(\s+\d+)?\s*",
        re.MULTILINE | re.DOTALL)
    rx_entity = re.compile(
        r"^\s+Chassis ID type\s+:(?P<chassis_id_type>.+)\s*\n"
        r"^\s+Chassis ID\s+:(?P<chassis_id>.+)\s*\n"
        r"^\s+System name\s+:(?P<system_name>.*)\n"
        r"^\s+System description\s+:(?P<system_description>(.|\n)*)\n"
        r"^\s+System capabilities supported\s+:(?P<system_capabilities>.+)\s*\n"
        r"^\s+System capabilities enabled\s+:(?P<system_capabilities_>.+)\s*\n"
        r"(^\s+Management address subtype\s+:(?P<mgmt_addr_type>.+)\s*\n)?"
        r"(^\s+Management address\s+:(?P<mgmt_addr>.+)\s*\n)?"
        r"(^\s+Interface numbering subtype\s+:(?P<interface_numbering_subtype>.+)\s*\n)?"
        r"(^\s+Interface number\s+:(?P<interface_number>.+)\s*\n)?"
        r"(^\s+Object identifier\s+:\s*\n)?"
        r"^\s+Port ID type\s+:(?P<port_id_type>.+)\s*\n"
        r"^\s+Port ID\s+:(?P<port_id>.+)\s*\n"
        r"^\s+Port description\s+:(?P<port_description>.*)\n",
        re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbor-information")
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
                    "mac address": 4,
                    "MAC address": 4,
                    "macaddress": 4,
                    "network address": 5,
                    "interface name": 6,
                    "local": 7
                }[m.group("chassis_id_type").strip().lower()]
                n["remote_chassis_id"] = m.group("chassis_id").strip()
                remote_port_subtype = m.group("port_id_type")
                remote_port_subtype.replace("_", " ")
                n["remote_port_subtype"] = {
                    "interface alias": 1,
                    "port component": 2,
                    "mac address": 3,
                    "macAddress": 3,
                    "network address": 4,
                    "interface name": 5,
                    "Interface Name": 5,
                    "Interface name": 5,
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
                    n["remote_port_description"] = \
                        m.group("port_description").strip()
                if m.group("system_name").strip():
                    n["remote_system_name"] = \
                        m.group("system_name").strip()
                if m.group("system_description").strip():
                    n["remote_system_description"] = \
                        m.group("system_description").strip()
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
                        "Station Only": 128
                    }[c]
                n["remote_capabilities"] = caps
                i["neighbors"] += [n]
            if i["neighbors"]:
                r += [i]
        return r
