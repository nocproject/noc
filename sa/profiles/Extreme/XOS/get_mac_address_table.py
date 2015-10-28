# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re

rx_line = re.compile(r"^(?P<mac>\S+)\s+\S+\((?P<vlan_id>\d+)\)\s+\d+\s+(?P<type>([dhmis\s]+))\s+?(?:\S+)?\s+(?P<interfaces>\d+)(?:\S+)?$")


class Script(BaseScript):
    name = "Extreme.XOS.get_mac_address_table"
    interface = IGetMACAddressTable
    TIMEOUT = 1900

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
                mactype = match.group("type")
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {"d m": "D", "dhm": "D","dhmi": "D", "d mi": "D", "s m": "S", "shm": "S"}[mactype.strip()]
                })
        return r
