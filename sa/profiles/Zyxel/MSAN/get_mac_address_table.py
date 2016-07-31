# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Zyxel.MSAN.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+"
        r"(?P<interface>.+)\s*$", re.MULTILINE)
    rx_port = re.compile(
        r"^Port: (?P<interface>\S+)\n"
        r"^index  vid mac\n"
        r"^----- ---- -----------------\n"
        r"(?P<macs>(^\s*\d+\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s*\n)+)",
        re.MULTILINE)
    rx_mac = re.compile(
        r"^\s*\d+\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s*",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac"
        if mac is not None:
            cmd += " %s" % mac
        if (interface is not None) and (interface.lower().startswith("enet")):
            cmd += " %s" % interface
        if vlan is not None:
            cmd += " vid %s" % vlan
        try:
            macs = self.cli(cmd)
            for match in self.rx_line.finditer(macs):
                mac_address = match.group("mac")
                iface = match.group("interface").replace(" ", "")
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [self.profile.convert_interface_name(iface)],
                    "type": "D"
                })
        except self.CLISyntaxError:
            macs = self.cli("statistics mac")
            for match in self.rx_port.finditer(macs):
                port = self.profile.convert_interface_name(match.group("interface"))
                for match1 in self.rx_mac.finditer(match.group("macs")):
                    r.append({
                        "vlan_id": match1.group("vlan_id"),
                        "mac": match1.group("mac"),
                        "interfaces": [port],
                        "type": "D"
                    })
        return r
