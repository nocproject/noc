# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s+"
        r"(?P<interfaces>\S+)\s+\S+$",  re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "display mac-address"
        if mac is not None:
            cmd += " %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
                iface = match.group("interfaces")
                # if iface == '0':
                #    continue
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [iface],
                    "type": {
                        "learned": "D",
                        "static": "S",
                        "permanent": "S",
                        "self": "C"
                        }[match.group("type").lower()]
                    })
        return r
