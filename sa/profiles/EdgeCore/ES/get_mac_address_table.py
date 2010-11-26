# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
##
## EdgeCore.ES.get_mac_address_table
##
class Script(NOCScript):
    name="EdgeCore.ES.get_mac_address_table"
    implements=[IGetMACAddressTable]
    
    rx_line1=re.compile(r"^\s*(?P<interface>Eth\s*\S+)\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)$", re.MULTILINE)
    rx_line2=re.compile(r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+(?:\S+)\s+(?P<interface>.+)$", re.MULTILINE)
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show mac-address-table"
        if mac is not None:
            cmd+=" address %s"%mac
        if interface is not None:
            cmd+=" interface %s"%interface
        if vlan is not None:
            cmd+=" vlan %s"%vlan
        macs=self.cli(cmd)
        r=[]
        rx=self.find_re([self.rx_line1, self.rx_line2], macs)
        for match in rx.finditer(macs):
            v=match.groupdict()
            r+=[{
                "vlan_id"   : v["vlan_id"],
                "mac"       : v["mac"],
                "interfaces": [v["interface"]],
                "type"      : {"learned":"D", "permanent":"S", "dynamic":"D", "static":"S"}[v["type"].lower()],
            }]
        return r
    
