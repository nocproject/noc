# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
from noc.sa.interfaces.base import MACAddressParameter
import re


class Script(noc.sa.script.Script):
    name = "DLink.DES21xx.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(
        r"^\d+\s+(?P<interfaces>\S+)\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)$")
    rx_line1 = re.compile(
        r"^\d+\s+(?P<interfaces>\d+)\s+(?P<mac>\S+)$")

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show fdb port "
        if interface is not None:
            cmd += "%s" % interface
            macs = self.cli(cmd)
        else:
            macs = ""
            for s in self.scripts.get_interface_status():
                macs += self.cli(cmd + "%s" % s["interface"])
        r = []
        for l in macs.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": "D"
                })
            else:
                match = self.rx_line1.match(l.strip())
                if match:
                    r.append({
                        "vlan_id": 1,
                        "mac": match.group("mac"),
                        "interfaces": [match.group("interfaces")],
                        "type": "D"
                    })
        # Static MAC address table
        macs = self.cli("show smac")
        for l in macs.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                iface = match.group("interfaces")
                if interface is not None:
                    if interface == iface:
                        r.append({
                            "vlan_id": match.group("vlan_id"),
                            "mac": match.group("mac"),
                            "interfaces": [iface],
                            "type": "S"
                        })
                else:
                    r.append({
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [iface],
                        "type": "S"
                    })
        return r
