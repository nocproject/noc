# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
from noc.lib.text import parse_table
import re


class Script(noc.sa.script.Script):
    name = "HP.GbE2.get_mac_address_table"
    implements = [IGetMACAddressTable]

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "/info/l2/fdb"
        if vlan:
            cmd += "/vlan %d" % vlan
            svlan = str(vlan)
        elif mac:
            cmd += "/find %s" % mac
        elif interface:
            cmd += "/port %s" % interface
        else:
            cmd += "/dump"
        r = []
        for m, v, port, trk, state in parse_table(self.cli(cmd)):
            if not m:
                continue
            if (not mac or m.upper() == mac) and (not vlan or v == svlan):
                p = trk if trk else port
                if interface and interface != p:
                    continue
                if v == "4095":  # Built-in vlans on port 19
                    continue
                r += [{
                    "vlan_id": v,
                    "mac": m,
                    "interfaces": [p],
                    "type": "D"
                }]
        return r
