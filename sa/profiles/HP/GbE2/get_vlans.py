# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

rx_vlan_line=re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s")

class Script(noc.sa.script.Script):
    name="HP.GbE2.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        vlans=self.cli("/i/l2/vlan")
        r=[]
        for l in vlans.split("\n"):
            match=rx_vlan_line.match(l.strip())
            if match:
                name=match.group("name")
                vlan_id=int(match.group("vlan_id"))
                if vlan_id not in [4095]:
                    r.append({"vlan_id": vlan_id,
                              "name"   : name})
        self.cli("/")
        return r
