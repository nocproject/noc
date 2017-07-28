# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Raisecom.ROS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"(?P<interface>(?:P|PC|port)?\d+)\s+"
        r"(?P<vlan_id>\d+)\s*(?P<type>Hit|Static|dynamic)",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        v = self.cli("show mac-address-table l2-address")
        r = []
        for match in self.rx_line.finditer(v):
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("interface")],
                "type": {
                    "hit": "D",
                    "dynamic": "D",
                    "static": "S"
                }[match.group("type").lower()]
            }]
        return r
