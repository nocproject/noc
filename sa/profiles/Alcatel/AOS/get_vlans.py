# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

rx_vlan_line=re.compile(r"^\s*(?P<vlan_id>\d{1,4})(\s+\S+){9}\s+(?P<name>(\S+\s*)+?)\s*$")

class Script(noc.sa.script.Script):
    name="Alcatel.AOS.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        vlans=self.cli("show vlan")
        r=[]
        for l in vlans.split("\n"):
            match=rx_vlan_line.match(l.strip())
            if match:
                name=match.group("name")
                r.append({"vlan_id": int(match.group("vlan_id")),
                          "name"   : name})
        return r
