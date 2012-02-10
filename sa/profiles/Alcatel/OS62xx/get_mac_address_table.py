# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.OS62xx.get_mac_address_table
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
    name = "Alcatel.OS62xx.get_mac_address_table"
    implements = [IGetMACAddressTable]

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show bridge address-table"
        if vlan:
            cmd += " vlan %d" % vlan
        if mac:
            cmd += " address %s" % mac
        if interface:
            if interface.lower().startswith("po"):
                cmd += " port-channel %s" % interface
            else:
                cmd += " ethernet %s" % interface
        r = []
        for v, m, port, type in parse_table(self.cli(cmd)):
            r += [{
                "vlan_id": v,
                "mac": m,
                "interfaces": [port],
                "type": {"dynamic": "D", "static": "S"}[type.lower()]
            }]
        return r
