# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

class Script(noc.sa.script.Script):
    name="DLink.DxS.get_vlans"
    implements=[IGetVlans]
    rx_vlan=re.compile(r"VID\s+:\s+(?P<vlanid>\S+).+VLAN Name\s+:\s+(?P<vlanname>\S+)",re.MULTILINE|re.DOTALL)
    def execute(self):
        vlans=self.cli("show vlan")
        r=[]
        for l in vlans.split("\n"):
            l=l.strip()
            match=self.rx_vlan.search(l)
            if match:
                r.append({"vlan_id":int(match.group('vlanid')),"name":match.group('vlanname')})
        return r
