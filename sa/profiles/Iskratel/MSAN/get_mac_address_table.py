# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Iskratel.MSAN.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Iskratel.MSAN.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s+"
        r"(?P<type>\S+)\s*\n", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-addr-table"
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if mac is not None:
            cmd += " %s" % mac
        macs = self.cli(cmd)
        r = []
        for match in self.rx_line.finditer(macs):
            if match.group("type") == "Learned":
                mtype = "D"
            else:
                mtype = "S"
            r.append({
                "vlan_id": int(match.group("vlan_id")),
                "mac": match.group("mac"),
                "interfaces": [match.group("interface")],
                "type": mtype
            })
        return r
