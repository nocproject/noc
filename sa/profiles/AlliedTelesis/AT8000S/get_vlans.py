# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

rx_vlan_line=re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s")

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8000S.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        vlans=self.cli("show vlan")
        r=[]
        for l in vlans.split("\n"):
            match=rx_vlan_line.match(l.strip())
            if match:
                name=match.group("name")
                vlan_id=int(match.group("vlan_id"))
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "name"   : match.group("name")
                    })
        return r