# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

rx_line=re.compile(r"^vlan \d+\s+(?P<interface>(?:\d/)?[ge]\d+)\s+(?P<ip>\S+)\s+(?P<mac>[\d:a-f]+)\s+")

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8000S.get_arp"
    implements=[IGetARP]
    def execute(self):
        s=self.cli("show arp")
        r=[]
        for l in s.split("\n"):
            match=rx_line.match(l.strip())
            if not match:
                continue
            r.append({
                "ip"        : match.group("ip"),
                "mac"       : match.group("mac"),
                "interface" : match.group("interface")
                })
        return r