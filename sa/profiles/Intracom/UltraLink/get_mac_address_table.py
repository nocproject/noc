# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Intracom.UltraLink.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Intracom.UltraLink.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac = re.compile(r"\d+\s+(?P<port>\S+)\s+(?P<vlan>\d+)\s+(?P<mac>\S+)")

    def execute_cli(self, **kwargs):
        fdb = []
        cli = self.cli("get fdb dynamic")
        for match in self.rx_mac.finditer(cli):
            fdb += [
                {
                    "vlan_id": match.group("vlan"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("port")],
                    "type": "D",
                }
            ]
        cli = self.cli("get fdb static")
        for match in self.rx_mac.finditer(cli):
            fdb += [
                {
                    "vlan_id": match.group("vlan"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("port")],
                    "type": "S",
                }
            ]
        return fdb
