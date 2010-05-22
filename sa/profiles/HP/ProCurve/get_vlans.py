# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

rx_vlan_sep=re.compile(r"^.+?\n\s*-{4,}\s+-{4,}\s+\+\s+-{4,}\s+-{4,}\s+-{4,}\n(.+)$",re.MULTILINE|re.DOTALL)
rx_vlan_line=re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<name>[^|]+?)\s+\|.+$")

class Script(noc.sa.script.Script):
    name="HP.ProCurve.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        vlans=self.cli("show vlans")
        match=rx_vlan_sep.match(vlans)
        vlans=match.group(1)
        r=[]
        for l in vlans.split("\n"):
            match=rx_vlan_line.match(l.strip())
            if match:
                name=match.group("name")
                vlan_id=int(match.group("vlan_id"))
                r.append({"vlan_id": vlan_id,
                          "name"   : name})
        return r
