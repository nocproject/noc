# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\d+\s+(?P<mac>\S+)\s+(?:sap|sdp):(?P<port>lag-\d+|\d+/\d+/\d+):"
        r"(?P<vlans>\S+)\s+(?P<type>\S)", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show service fdb-mac"
        if mac is not None:
            cmd += " %s" % mac
        cmd += " | match invert-match ["
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            vlans = match.group("vlans")
            if "." in vlans and "*" not in vlans:
                up_tag, down_tag = vlans.split(".")
                vlan_id = int(up_tag)
            elif "*" in vlans:
                vlan_id = 1
            else:
                vlan_id = int(vlans)
            r += [{
                "vlan_id": vlan_id,
                "mac": match.group("mac"),
                "interfaces": [match.group("port")],
                "type": {
                    "L": "D",  # Learned
                    "O": "D",  # OAM
                    "P": "S",  # Protected
                    "C": "S",  # Conditional
                    "S": "S",  # Static
                }[match.group("type")]
            }]
        return r
