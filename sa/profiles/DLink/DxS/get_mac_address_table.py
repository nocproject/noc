# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

class Script(noc.sa.script.Script):
    name="DLink.DxS.get_mac_address_table"
    implements=[IGetMACAddressTable]
    rx_line=re.compile(r"^(?P<vlan_id>\d+)\s+\S+\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)$")
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show fdb" 
        if mac is not None:
            cmd+=" mac_address %s"%mac
        if interface is not None:
            cmd+=" port %s"%interface
        if vlan is not None:
            cmd+=" vlanid %s"%vlan
        macs=self.cli(cmd)
        r=[]
        for l in macs.split("\n"):
            match=self.rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"dynamic":"D","static":"S"}[match.group("type").lower()],
                })
        return r
