# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
##
##  This is a draft variant
##  I need to find some missing values
##

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.sa.interfaces.base import IPv4Parameter
from noc.lib.validators import is_int, is_ipv4
import re
import binascii


class Script(BaseScript):
    name = "DLink.DxS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(r"\n\nPort ID\s+:\s+", re.MULTILINE)
    rx_id = re.compile(r"^(?P<port_id>\S+)", re.MULTILINE)
    rx_re_ent = re.compile(r"Remote Entities Count\s+:\s+(?P<re_ent>\d+)",
        re.MULTILINE | re.IGNORECASE)
    rx_line1 = re.compile(r"\s*Entity\s+\d+")
    rx_remote_chassis_id_subtype = re.compile(
        r"Chassis ID Subtype\s+: (?P<subtype>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_chassis_id = re.compile(r"Chassis ID\s+: (?P<id>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id_subtype = re.compile(
        r"Port ID Subtype\s+: (?P<subtype>.+)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port_id = re.compile(r"Port ID\s+: (?P<port>.+)",
        re.IGNORECASE)
    rx_remote_port_id2 = re.compile(r"RMON Port (?P<port>\d+([/:]\d+)?)",
        re.IGNORECASE)
    rx_remote_port_id3 = re.compile(
        r"Port Description\s+: D-Link D[EGX]S-\S+\s+\S+\s+Port\s+(?P<port>\d+)")
    rx_remote_port_id4 = re.compile(
        r"Port Description\s+: (?P<port>((Ten)?Gigabit|Fast)?Ethernet\d+\S+)")
    rx_remote_system_name = re.compile(r"System Name\s+: (?P<name>.+)",
        re.IGNORECASE)
    rx_remote_capabilities = re.compile(
        r"System Capabilities\s+: (?P<capabilities>.+)",
        re.MULTILINE | re.IGNORECASE)

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
            match = self.rx_re_ent.search(s)
            if not match:
                continue
            # Remote Entities Count : 0
            if match.group("re_ent") == "0":
                continue
            i = {"local_interface": port_id, "neighbors": []}
            # For each neighbor
            for s1 in self.rx_line1.split(s)[1:]:
                n = {}

                # remote_chassis_id_subtype
                match = self.rx_remote_chassis_id_subtype.search(s1)
                if not match:
                    # Debug string
                    self.logger.debug('remote_chassis_id_subtype is empty!')
                    continue
                remote_chassis_id_subtype = match.group("subtype").strip()
                n["remote_chassis_id_subtype"] = {
                    "Chassis Component": 1,
                    "Interface Alias": 2,
                    "Port Component": 3,
                    "MAC Address": 4,
                    "macaddress": 4,
                    "Network Address": 5,
                    "Interface Name": 6,
                    "Local": 7,
                    "local": 7
                }[remote_chassis_id_subtype]

                # remote_chassis_id
                match = self.rx_remote_chassis_id.search(s1)
                if not match:
                    # Debug string
                    self.logger.debug('remote_chassis_id is empty!')
                    continue
                n["remote_chassis_id"] = match.group("id").strip()

                # remote_port_subtype
                match = self.rx_remote_port_id_subtype.search(s1)
                if not match:
                    # Debug string
                    self.logger.debug('remote_port_id_subtype is empty!')
                    continue
                remote_port_subtype = match.group("subtype").strip()
                n["remote_port_subtype"] = {
                    "Interface Alias": 1,
                    "INTERFACE_ALIAS": 1,
                    # DES-3526 6.00 B48 and DES-3526 6.00 B49
                    "NTERFACE_ALIAS": 1, 
                    "Port Component": 2,
                    "MAC Address": 3,
                    "macaddress": 3,
                    "Network Address": 4,
                    "Interface Name": 5,
                    "INTERFACE_NAME": 5,
                    "Agent Circuit ID": 6,
                    "Local": 7,
                    "local": 7
                }[remote_port_subtype]

                # remote_port
                match = self.rx_remote_port_id.search(s1)
                if not match:
                    # Try to parse string like
                    # Port Description : D-Link DGS-3627G R3.00.B27 Port 23
                    # Port Description : D-Link DGS-3120-24SC R2.00.B01 Port 2 on Unit 1
                    match = self.rx_remote_port_id3.search(s1)
                    if match:
                        n["remote_port_subtype"] = 5
                    else:
                        # Debug string
                        self.logger.debug('remote_port_id is empty!')
                        continue

                n["remote_port"] = match.group("port").strip()
                # Interface Alias
                if n["remote_port_subtype"] == 1:
                    match = self.rx_remote_port_id4.search(s1)
                    if match:
                        # Dirty hack !
                        n["remote_port_subtype"] = 5
                        n["remote_port"] = match.group("port")
                # MAC Address
                if n["remote_port_subtype"] == 3:
                    # Try to convert to Interface Name
                    match = self.rx_remote_port_id3.search(s1)
                    if match:
                        n["remote_port_subtype"] = 5
                        n["remote_port"] = match.group("port")
                    else:
                        try:
                            n["remote_port"] = \
                                MACAddressParameter().clean(n["remote_port"])
                        except:
                            pass
                # IP Address
                if n["remote_port_subtype"] == 4:
                    n["remote_port"] = \
                        IPv4Parameter().clean(n["remote_port"])
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
                        self.logger.debug('Invalid remote_port_id!')
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
                    for c in match.group("capabilities").split(","):
                        c = c.strip()
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
            r += [i]
        return r
