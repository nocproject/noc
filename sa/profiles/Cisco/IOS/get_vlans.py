# -*- coding: utf-8 -*-
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
    name="Cisco.IOS.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        self.cli("terminal length 0")
        vlans=self.cli("show vlan brief")
        r=[]
        for l in vlans.split("\n"):
            match=rx_vlan_line.match(l.strip())
            if match:
                name=match.group("name")
                if name in ["fddi-default","trcrf-default","fddinet-default","trbrf-default"]:
                    continue
                r.append({"vlan_id": int(match.group("vlan_id")),
                          "name"   : name})
        return r
