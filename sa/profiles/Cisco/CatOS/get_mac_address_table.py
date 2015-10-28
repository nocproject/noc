# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.CatOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
import noc.sa.profiles
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re

rx_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<mac>\S+)\s+(?:(?P<type>\S+)\s)?(?P<interfaces>(?:\d|\/|-|,)+)\s+\S+$")


class Script(BaseScript):
    name = "Cisco.CatOS.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show cam"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
            if vlan is not None:
                cmd += " %s" % vlan
        elif interface is not None:
            cmd += " dynamic %s" % interface
        elif vlan is not None:
            cmd += " dynamic %s" % vlan
        else:
            cmd += " dynamic"
        vlans = self.cli(cmd)
        r = []
        for l in vlans.split("\n"):
            match = rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": "D"
                })
        return r
