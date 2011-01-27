# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES2108.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re

class Script(NOCScript):
    name="DLink.DES2108.get_vlans"
    implements=[IGetVlans]
    rx_vlan=re.compile(r"VLAN_ID:(?P<vlanid>\d+)\nVLAN name:(?P<vlanname>\S+)\n", re.MULTILINE|re.DOTALL)
    def execute(self):
        r=[]
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r+=[{
                "vlan_id" : int(match.group('vlanid')),
                "name"    : match.group('vlanname')
            }]
        return r
