# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac"
        if interface is not None:
            cmd += " interface %s" % interface
        else:
            cmd += " all"
        t = parse_table(self.cli(cmd))
        for i in t:
            r += [{
                "vlan_id": int(i[1]),
                "mac": i[2],
                "interfaces": [i[3]],
                "type": "D"
            }]
        return r
