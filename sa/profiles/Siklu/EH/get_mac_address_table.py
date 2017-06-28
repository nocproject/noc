# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Siklu.EH.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self):
        v = self.cli("show fdb-table all")
        r = []
        for l in v.splitlines():
            parts = l.split()
            if parts and parts[0] == "s1" and parts[-1] == "learned":
                r += [{
                    "vlan_id": 1,
                    "mac": parts[2],
                    "interfaces": [parts[3]],
                    "type": "D"
                }]
        return r
