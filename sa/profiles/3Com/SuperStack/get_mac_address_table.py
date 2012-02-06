# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 3Com.SuperStack.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
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
    name = "3Com.SuperStack.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_line = re.compile(r"^Port\s+(?P<interfaces>\d+)\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)$", re.MULTILINE)
    rx_line2 = re.compile(r"^Unit\s+(?P<unit>\d+)\s+Port\s+(?P<interfaces>\d+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "bridge port address list"
        if interface is not None:
            cmd += " %s" % interface
        else:
            cmd += " all"
        if mac is not None:
            cmd = "bridge port address find %s" % self.profile.convert_mac(mac)
        macs = self.cli(cmd)
        r = []
        if mac is None:
            rx = self.rx_line
        else:
            rx = self.rx_line2
        for match in rx.finditer(macs):
            vid = int(match.group("vlan_id"))
            if vlan is None or vid == vlan:
                r += [{
                    "vlan_id": vid,
                    "mac": mac if mac else match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {"no":"D", "yes":"S"}[match.group("type").lower()]
                }]
        return r
