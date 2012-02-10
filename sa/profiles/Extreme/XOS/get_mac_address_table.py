# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line = re.compile(r"^(?P<mac>\S+)\s+\S+\((?P<vlan_id>\d+)\)\s+\d+\s+(?P<type>(?:(?:\S)(?:\s))+)\s+(?P<interfaces>.*)$")


class Script(noc.sa.script.Script):
    name = "Extreme.XOS.get_mac_address_table"
    implements = [IGetMACAddressTable]

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show fdb"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " ports %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        vlans = self.cli(cmd)
        r = []
        for l in vlans.split("\n"):
            match = rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {"d m ": "D", "s m ": "S"}[match.group("type")]
                })
        return r
