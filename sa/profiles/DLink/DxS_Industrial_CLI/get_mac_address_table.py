# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.text import parse_table


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        v = self.cli(cmd)
        r = []
        t = parse_table(v)
        for i in t:
            if i[3] == "CPU":
                continue
            r += [
                {
                    "vlan_id": i[0],
                    "mac": i[1],
                    "interfaces": [i[3]],
                    "type": {"dynamic": "D", "static": "S"}[i[2].lower()],
                }
            ]
        return r
