# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES2108.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

class Script(noc.sa.script.Script):
    name="DLink.DES2108.get_vlans"
    implements=[IGetVlans]
    rx_vlan=re.compile(r"VLAN_ID:(?P<vlanid>\d+)\nVLAN name:(?P<vlanname>\S+)\n", re.MULTILINE|re.DOTALL)
    def execute(self):
        r=[]
        v=self.cli("show vlan")
        for match in self.rx_vlan.finditer(v):
            r+=[{
                "vlan_id" : int(match.group('vlanid')),
                "name"    : match.group('vlanname')
            }]
        return r
