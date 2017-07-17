# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Carelink.SWG.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Carelink.SWG.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        c = self.cli("show mac-address-table")
        for i in parse_table(c, max_width=80):
            mtype = i[0].lower()
            vlan_id = i[1]
            if (vlan is not None) and (vlan != vlan_id):
                continue
            mmac = i[2]
            if (mac is not None) and (mac != mmac):
                continue
            port = i[3]
            if "None" in port:
                continue
            ports = self.expand_rangelist(port.replace(",CPU", ""))
            r += [{
                "vlan_id": vlan_id,
                "mac": mmac,
                "interfaces": ports,
                "type": {
                    "dynami": "D",
                    "static": "S",
                }[mtype],
            }]
        return r
