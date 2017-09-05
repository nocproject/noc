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
from noc.sa.interfaces.base import MACAddressParameter
import re


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx..get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<mac>[0-9a-f ]{2}:[0-9a-f ]{2}:[0-9a-f ]{2}:[0-9a-f ]{2}:"
        r"[0-9a-f ]{2}:[0-9a-f ]{2})\s{2,}(?P<vlan_id>\d+)\s+"
        r"(?P<interface>\d+\S+)\s+\d+\s*\n",
        re.MULTILINE
    )

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        for match in self.rx_line.finditer(self.cli("show fdb")):
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac").replace(" ", ""),
                "interfaces": [match.group("interface")],
                "type": "D"
            }]
        return r
