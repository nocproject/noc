# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Eltex.MES5448.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-addr-table"
        if mac is not None:
            cmd += " %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for i in parse_table(self.cli(cmd)):
            r += [{
                "vlan_id": i[0],
                "mac": i[1],
                "interfaces": [i[2]],
                "type": {
                    "Learned": "D",
                    "Management": "C"
                }[i[4]],
            }]
        return r
