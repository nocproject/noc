# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

rx_line=re.compile(r"^(?P<mac>[0-9a-f]\S+)\s+(?P<ip>\S+)\s+\S+\s+(?P<interface>\S+)\s+\S+")

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_arp"
    implements=[IGetARP]
    def execute(self):
        self.cli("set cli screen-length 0")
        s=self.cli("show arp")
        r=[]
        for l in s.split("\n"):
            match=rx_line.match(l.strip())
            if not match:
                continue
            mac=match.group("mac")
            r.append({"ip":match.group("ip"),"mac":match.group("mac"),"interface":match.group("interface")})
        return r
