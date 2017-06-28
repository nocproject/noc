# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.MINI_LINK.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Ericsson.MINI_LINK.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address-table"
        #if mac is not None:
        #    cmd += " address %s" % mac
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        r = []
        t = parse_table(self.cli_clean(cmd), footer="^Showing")
        for i in t:
            r += [{
                "vlan_id": i[0],
                "mac": i[1],
                "interfaces": [i[3]],
                "type": "D" if i[2] == "learned" else "S"
            }]
        return r
