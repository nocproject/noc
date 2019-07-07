# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<mac>([0-9a-f ]{2}:){5}[0-9a-f ]{2})\s{2,}(?P<vlan_id>\d+)\s+"
        r"(?P<interface>\d+\S+)\s+\d+\s*\n",
        re.MULTILINE,
    )
    rx_line_9806h = re.compile(
        r"^\s*(?P<interface>\d+/\d+)\s+(?P<mac>([0-9A-F]{2}-){5}[0-9A-F]{2})\s+"
        r"(?P<vlan_id>\d+)\s+",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        if self.is_9806h:
            v = self.cli("show mac-address-table")
            rx_line = self.rx_line_9806h
        else:
            v = self.cli("show fdb")
            rx_line = self.rx_line
        r = []
        for match in rx_line.finditer(v):
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac").replace(" ", ""),
                    "interfaces": [match.group("interface")],
                    "type": "D",
                }
            ]
        return r
