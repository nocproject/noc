# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"^vlan \d+\s+(?P<interface>(?:\d/)?[ge]\d+)\s+(?P<ip>\S+)\s+(?P<mac>[\d:a-f]+)\s+")

    def execute(self):
        s = self.cli("show arp")
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            r.append({
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
                })
        return r
