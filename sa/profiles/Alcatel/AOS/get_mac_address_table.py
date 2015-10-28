# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re

rx_line = re.compile(
    r"^\s*VLAN\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)"
    r"\s+\S+\s+\S+\s+(?P<interfaces>\S+)", re.MULTILINE)


class Script(BaseScript):
    name = "Alcatel.AOS.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self):
        v = self.cli("show mac-address-table")
        r = []
        for match in rx_line.finditer(v):
            mac = match.group("mac")
            if mac == "*":
                continue
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": mac,
                "interfaces": [match.group("interfaces")],
                "type": {
                    "learned":"D",
                    "permanent":"S"
                }[match.group("type").lower()]
            }]
        return r
