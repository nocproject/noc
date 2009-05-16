# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

rx_line=re.compile(r"^Internet\s+(?P<ip>\S+)\s+\d+\s+(?P<mac>\S+)\s+\S+(?:\s+(?P<interface>\S+))")

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_arp"
    implements=[IGetARP]
    def execute(self):
        self.cli("terminal length 0")
        s=self.cli("show arp")
        r=[]
        for l in s.split("\n"):
            match=rx_line.match(l.strip())
            if not match:
                continue
            mac=match.group("mac")
            if mac.lower()=="incomplete":
                r.append({"ip":match.group("ip"),"mac":None,"interface":None})
            else:
                r.append({"ip":match.group("ip"),"mac":match.group("mac"),"interface":match.group("interface")})
        return r
