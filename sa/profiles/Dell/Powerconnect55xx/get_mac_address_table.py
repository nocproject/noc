# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s+"
        r"(?P<type>\S+)\s*$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %d" % vlan
        if mac is not None:
            cmd += " address %d" % vlan
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            interface = match.group("interface")
            if interface == "0":
                continue
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [interface],
                "type": {
                    "dynamic":"D",
                    "static":"S"
                }[match.group("type").lower()]
            }]
        return r
