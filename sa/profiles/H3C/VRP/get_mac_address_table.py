# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "H3C.VRP.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_vrp3line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+"
        r"(?P<type>Learned|Config static)\s+(?P<interfaces>[^ ]+)\s{2,}"
    )
    rx_vrp5line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?:\S+)\s+(?:\S+)\s+"
        r"(?P<interfaces>\S+)\s+(?P<type>dynamic|static)\s+"
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "display mac-address"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        rx_line = self.rx_vrp3line
        r = []
        for l in self.cli(cmd).splitlines():
            match = rx_line.match(l.strip())
            if match:
                if vlan is not None and int(match.group("vlan_id")) != vlan:
                    continue
                if interface is not None and match.group("interfaces") != interface:
                    continue
                r += [{
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {
                        "dynamic": "D",
                        "static": "S",
                        "learned": "D",
                        "Config static": "S"
                    }[match.group("type").lower()]
                }]
        return r
