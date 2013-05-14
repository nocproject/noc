# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "Arista.EOS.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+"
        r"(?P<type>DYNAMIC|STATIC)\s+(?P<interfaces>\S+)"
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            # @todo: Fix
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        r = []
        macs = self.cli(cmd)
        for l in macs.splitlines():
            l = l.strip()
            if l.startswith("Multicast"):
                break
            match = self.rx_line.match(l)
            if match:
                mac = match.group("mac")
                interfaces = [
                    i.strip()
                    for i in match.group("interfaces").split(",")
                ]
                if not interfaces:
                    continue
                m_type = {
                    "dynamic": "D",
                    "static": "S"
                }.get(match.group("type").lower())
                if not m_type:
                    continue
                r += [{
                    "vlan_id": match.group("vlan_id"),
                    "mac": mac,
                    "interfaces": interfaces,
                    "type": m_type
                }]
        return r
