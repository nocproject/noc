# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
##
##  This is a draft variant
##  I need to find some missing values
##

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_line = re.compile(r"\w*Lldp neighbor-information of port \[",
        re.MULTILINE)
    rx_id = re.compile(r"^(?P<port_id>.+)\]",
        re.MULTILINE)
    rx_re_ent = re.compile(r"Remote Entities Count\s+:\s+(?P<re_ent>\d+)",
        re.MULTILINE | re.IGNORECASE)
    rx_line1 = re.compile(r"\s*Neighbor index\s+")
    rx_remote_chassis_id_subtype = re.compile(
        r"Chassis ID type\s+: (?P<subtype>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_chassis_id = re.compile(r"Chassis ID\s+: (?P<id>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id_subtype = re.compile(r"Port ID type\s+: (?P<subtype>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id = re.compile(r"Port ID\s+: (.*[:/])*(?P<port>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id2 = re.compile(r"RMON Port (.*[:/])*(?P<port>\d+)",
        re.IGNORECASE)
    rx_remote_system_name = re.compile(r"System name\s+: (?P<name>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_capabilities = re.compile(
        r"System capabilities supported\s+: (?P<capabilities>.+)",
        re.MULTILINE | re.IGNORECASE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbor-information")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
<<<<<<< HEAD
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
=======
        v = "\n" + v
        # For each interface
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_id.search(s)
            if not match:
                continue
            port_id = match.group("port_id")
            i = {"local_interface": port_id, "neighbors": []}
            # For each neighbor
            for s1 in self.rx_line1.split(s)[1:]:
                n = {}

                # remote_chassis_id_subtype
                match = self.rx_remote_chassis_id_subtype.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_chassis_id_subtype\n\n\n\n\n"
                    continue
                remote_chassis_id_subtype = match.group("subtype").strip()
                # TODO: Find other subtypes
                # 0 is reserved
                if remote_chassis_id_subtype == "Chassis Component":
                    n["remote_chassis_id_subtype"] = 1
                elif remote_chassis_id_subtype == "Interface Alias":
                    n["remote_chassis_id_subtype"] = 2
                elif remote_chassis_id_subtype == "Port Component":
                    n["remote_chassis_id_subtype"] = 3
                elif remote_chassis_id_subtype == "MAC Address":
                    n["remote_chassis_id_subtype"] = 4
                elif remote_chassis_id_subtype == "MAC address":
                    n["remote_chassis_id_subtype"] = 4
                elif remote_chassis_id_subtype == "Locally assigned":
                    n["remote_chassis_id_subtype"] = 4
                elif remote_chassis_id_subtype.lower() == "macaddress":
                    n["remote_chassis_id_subtype"] = 4
                elif remote_chassis_id_subtype == "Network Address":
                    n["remote_chassis_id_subtype"] = 5
                elif remote_chassis_id_subtype == "Interface Name":
                    n["remote_chassis_id_subtype"] = 6
                elif remote_chassis_id_subtype == "Interface name":
                    n["remote_chassis_id_subtype"] = 6
                elif remote_chassis_id_subtype == "Locally assigned":
                    n["remote_chassis_id_subtype"] = 7
                elif remote_chassis_id_subtype.lower() == "local":
                    n["remote_chassis_id_subtype"] = 7
                # 8-255 are reserved

                # remote_chassis_id
                match = self.rx_remote_chassis_id.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_chassis_id\n\n\n\n\n"
                    continue
                n["remote_chassis_id"] = match.group("id").strip()

                # remote_port_subtype
                match = self.rx_remote_port_id_subtype.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_port_id_subtype\n\n\n\n\n"
                    continue
                remote_port_subtype = match.group("subtype").strip()
                # TODO: Find other subtypes
                # 0 is reserved
                if remote_port_subtype == "Interface Alias":
                    n["remote_port_subtype"] = 1
                elif remote_port_subtype == "Port Component":
                    n["remote_port_subtype"] = 2
                elif remote_port_subtype == "MAC Address":
                    n["remote_port_subtype"] = 3
                elif remote_port_subtype == "MAC address":
                    n["remote_port_subtype"] = 3
                elif remote_port_subtype == "Network Address":
                    n["remote_port_subtype"] = 4
                elif remote_port_subtype == "Interface Name":
                    n["remote_port_subtype"] = 5
                elif remote_port_subtype == "Interface name":
                    n["remote_port_subtype"] = 5
                elif remote_port_subtype == "Agent Circuit ID":
                    n["remote_port_subtype"] = 6
                elif remote_port_subtype == "Locally assigned":
                    n["remote_port_subtype"] = 7
                elif remote_port_subtype.lower() == "local":
                    n["remote_port_subtype"] = 7
                # 8-255 are reserved

                # remote_port
                match = self.rx_remote_port_id.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_port_id\n\n\n\n\n"
                    continue
                n["remote_port"] = match.group("port").strip()

                if n["remote_port_subtype"] == 7 \
                and n["remote_port"].lower().startswith("rmon port"):
                    match = self.rx_remote_port_id2.search(n["remote_port"])
                    if not match:
                        # Debug string
                        print "\n\n\n\n\nInvalid remote_port_id\n\n\n\n\n"
                        continue
                    n["remote_port"] = match.group("port")

                # remote_system_name
                match = self.rx_remote_system_name.search(s1)
                if match:
                    remote_system_name = match.group("name").strip()
                    if remote_system_name != "":
                        n["remote_system_name"] = remote_system_name

                # remote_capabilities
                caps = 0
                match = self.rx_remote_capabilities.search(s1)
                if match:
                    remote_capabilities = match.group("capabilities").strip()
                    # TODO: Find other capabilities
                    if remote_capabilities.find("Other") != -1:
                        caps += 1
                    if remote_capabilities.find("Repeater") != -1:
                        caps += 2
                    if remote_capabilities.find("Bridge") != -1:
                        caps += 4
                    if remote_capabilities.find("WLAN Access Point") != -1:
                        caps += 8
                    if remote_capabilities.find("Router") != -1:
                        caps += 16
                    if remote_capabilities.find("Telephone") != -1:
                        caps += 32
                    if remote_capabilities.find("DOCSIS Cable Device") != -1:
                        caps += 64
                    if remote_capabilities.find("Station Only") != -1:
                        caps += 128
                # 8-15 bits are reserved
                n["remote_capabilities"] = caps

                i["neighbors"] += [n]
            r += [i]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
