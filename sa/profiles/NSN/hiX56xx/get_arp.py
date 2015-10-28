# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NSN.hiX56xx.get_arp
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "NSN.hiX56xx.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        "^(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\S+\s+(?P<interface>\S+)$")

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
