# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>[:0-9a-fA-F]+)\s+(?P<interfaces>(?:\d/)?[ge]\d+)\s+(?P<type>\w+)$")

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show bridge address-table"
        if mac is not None:
            cmd += " address %s" % mac
        # interface option not working for port-channel trunks
        if interface is not None:
            cmd += " ethernet %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        self.cli("terminal datadump")
        vlans = self.cli(cmd)
        vlans = self.strip_first_lines(vlans, 4)
        r = []
        for l in vlans.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {"dynamic": "D",
                        "static": "S"}[match.group("type")],
                })
        return r
