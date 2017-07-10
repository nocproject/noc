# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.AOS.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Alcatel.AOS.get_mac_address_table"
    interface = IGetMACAddressTable
    TIMEOUT = 600

    rx_line = re.compile(
        r"^(\s*VLAN)?\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)"
        r"\s+\S+\s+\S+\s+(?P<interfaces>\S+)", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        v = self.cli("show mac-address-table")
        r = []
        for match in self.rx_line.finditer(v):
            mac = match.group("mac")
            if mac == "*":
                continue
            iface = match.group("interfaces")
            if iface.startswith("0/"):
                # LAG 0/1 -> Ag 1
                iface = "Ag %s" % iface[2:]
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": mac,
                "interfaces": [iface],
                "type": {
                    "learned": "D",
                    "permanent": "S"
                }[match.group("type").lower()]
            }]
        return r
