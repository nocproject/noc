# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
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
    name = "DLink.DGS3100.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_line = re.compile(r"\n\nPort ID\s+:\s+", re.MULTILINE)
    rx_id = re.compile(r"^(?P<port_id>\S+)", re.MULTILINE)
    rx_re_ent = re.compile(r"Remote Entities Count\s+:\s+(?P<re_ent>\d+)", re.MULTILINE | re.IGNORECASE)
    rx_line1 = re.compile(r"\s*Entity\s+\d+")
    rx_remote_chassis_id_subtype = re.compile(r"Chassis ID Subtype\s+: (?P<subtype>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_chassis_id = re.compile(r"Chassis ID\s+: (?P<id>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id_subtype = re.compile(r"Port ID Subtype\s+: (?P<subtype>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id = re.compile(r"Port ID\s+:\s+(\d+[/])?(?P<port>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id2 = re.compile(r"RMON Port (.*[:/])*(?P<port>\d+)", re.IGNORECASE)
    rx_remote_system_name = re.compile(r"System Name\s+: (?P<name>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_capabilities = re.compile(r"System Capabilities\s+: (?P<capabilities>.+)", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp remote_ports mode normal")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
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
                elif remote_chassis_id_subtype.lower() == "macaddress":
                    n["remote_chassis_id_subtype"] = 4
                elif remote_chassis_id_subtype == "Network Address":
                    n["remote_chassis_id_subtype"] = 5
                elif remote_chassis_id_subtype == "Interface Name":
                    n["remote_chassis_id_subtype"] = 6
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
                elif remote_port_subtype == "Network Address":
                    n["remote_port_subtype"] = 4
                elif remote_port_subtype == "Interface Name":
                    n["remote_port_subtype"] = 5
                elif remote_port_subtype == "Agent Circuit ID":
                    n["remote_port_subtype"] = 6
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
                '''
                Possible variants of Port ID, if Remote Port ID is "Local":
                Big thanks to D-Link developers :)
                >>> DGS-3100 Series
                1:2
                >>> DES-3526/3550 Series
                1/2
                >>> DES-3028/3052 Series
                RMON Port 2 on Unit 1
                >>> Other switches
                2
                '''
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
        return r
