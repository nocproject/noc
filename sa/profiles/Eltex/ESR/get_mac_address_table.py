# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Eltex.ESR.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        c = self.cli("show mac address-table")
        for vlan_id, mac, port, mtype in parse_table(c, footer="\d+ valid mac entries"):
            r += [{
                "vlan_id": vlan_id,
                "mac": mac,
                "interfaces": [port],
                "type": {
                    "dynamic": "D",
                    "static": "S",
                    "permanent": "S",
                    "self": "S"
                }[mtype.lower()],
            }]
        return r
