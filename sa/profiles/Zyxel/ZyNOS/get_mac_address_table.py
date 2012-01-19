# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_line = re.compile(r"^(?P<interfaces>\d+)\s+(?P<vlan_id>\d+)\s+" \
                          "(?P<mac>\S+)\s+(?P<type>\S+)\s*$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if interface is not None:
            cmd += " port %s" % interface
        elif vlan is not None:
            cmd += " vlan %s" % vlan
        else:
            cmd += " all"
        macs = self.cli(cmd)
        r = []
        for match in self.rx_line.finditer(macs):
            mac_address = match.group("mac")
            if mac is not None and mac.lower() != mac_address:
                continue
            r.append({
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("interfaces")],
                "type": {"Dynamic": "D",
                         "Static": "S"}[match.group("type")],
            })

        return r
