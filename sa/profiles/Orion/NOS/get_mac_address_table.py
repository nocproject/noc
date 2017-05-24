# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Orion.NOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_port = re.compile(
        r"^\s*(?P<port>\d+)", re.MULTILINE)
    rx_line = re.compile(
        r"^\s*(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+\S+\s*\n", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # "show mac address-table" command do not show port name on some cases
        for match in self.rx_port.finditer(self.cli("show port-security")):
            port = match.group("port")
            v = self.cli("show mac-address-table l2-address port %s" % port)
            for match1 in self.rx_line.finditer(v):
                r += [{
                    "vlan_id": match1.group("vlan_id"),
                    "mac": match1.group("mac"),
                    "interfaces": [port],
                    "type": "D"
                }]
        return r
