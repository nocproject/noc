# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "HP.ProCurve.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_fdb_vlan = re.compile(r"dot1qVlanFdbId\.\d+\.(\d+)\s*=\s*(\d+)")
    rx_line = re.compile(r"dot1qTpFdbPort\.(\d+)\.(\S+)\s*=\s*(\d+)")
    rx_if = re.compile(r"ifName\.(\d+)\s*=\s*(\S+)")

    def execute(self, interface=None, vlan=None, mac=None):
        # Build FDB VLAN ID-> VLAN ID mapping
        fdb_vmap = {}
        for match in self.rx_fdb_vlan.finditer(self.cli("walkMIB dot1qVlanFdbId")):
            fdb_vmap[match.group(2)] = int(match.group(1))
        # Build ifIndex -> port name mapping
        ifindex = {}
        for match in self.rx_if.finditer(self.cli("walkMIB ifName")):
            ifindex[match.group(1)] = match.group(2)
        # Get through vlans
        r = []
        for match in self.rx_line.finditer(self.cli("walkMIB dot1qTpFdbPort")):
            port = match.group(3)
            if port == "0" or port not in ifindex:
                continue
            port = ifindex[port]
            vlan_id = fdb_vmap[match.group(1)]
            m = ":".join(["%02X" % int(x) for x in match.group(2).split(".")])
            if (interface and interface != port) \
            or (vlan and vlan != vlan_id) or (mac and mac != m):
                continue
            r += [{
                "vlan_id": vlan_id,
                "mac": m,
                "interfaces": [port],
                "type": "D"
            }]
        return r
