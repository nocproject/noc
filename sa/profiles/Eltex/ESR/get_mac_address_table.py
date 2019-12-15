# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.ESR.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        c = self.cli("show mac address-table")
        for vlan_id, mac, port, mtype in parse_table(c, footer=r"\d+ valid mac entries"):
            r += [
                {
                    "vlan_id": vlan_id,
                    "mac": mac,
                    "interfaces": [port],
                    "type": {"dynamic": "D", "static": "S", "permanent": "S", "self": "S"}[
                        mtype.lower()
                    ],
                }
            ]
        return r
