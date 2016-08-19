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
    rx_line1 = re.compile(
        '^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+'
        '\S+\s+\S+\s+(?P<port>lag-\d+|\d+/\d+/\d+):(?P<vlans>\S+)$')
    rx_ies = re.compile('^(\d+)\s+IES\s+Up\s+Up', re.MULTILINE)

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
        v = self.cli('show service service-using ies')
        ies = self.rx_ies.findall(v)
        v = ""
        for vrf_id in ies:
            v += self.cli('show service id %s arp' % vrf_id)
        for l in v.split("\n"):
            match = self.rx_line1.match(l.strip())
            if not match:
                continue
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
                    "Dynamic": "D",
                    "Other": "D"
                }[match.group("type")]
            }]
        return r
