# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line=re.compile(r"^(?P<interfaces>\d+)\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)$")

class Script(noc.sa.script.Script):
    name="Zyxel.ZyNOS.get_mac_address_table" 
    implements=[IGetMACAddressTable]
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show mac address-table" 
        if interface is not None:
            cmd+=" port %s"%interface
        elif vlan is not None:
            cmd+=" vlan %s"%vlan
        else:
            cmd+=" all"
        macs=self.cli(cmd)
        r=[]
        for l in macs.split("\n"):
            match=rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"Dynamic":"D","Static":"S"}[match.group("type")],
                })
        return r
