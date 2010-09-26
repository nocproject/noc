# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES4xxx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line=re.compile(r"^(?P<interfaces>.+)\s(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s(?P<type>.*)$")

class Script(noc.sa.script.Script):
    name="EdgeCore.ES4xxx.get_mac_address_table"
    implements=[IGetMACAddressTable]
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show mac-address-table"
        if mac is not None:
            cmd+=" address %s"%mac
        if interface is not None:
            cmd+=" interface %s"%interface
        if vlan is not None:
            cmd+=" vlan %s"%vlan
        vlans=self.cli(cmd)
        r=[]
        for l in vlans.splitlines():
            match=rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"learned":"D","permanent":"S"}[match.group("type").lower()],
                })
        return r
