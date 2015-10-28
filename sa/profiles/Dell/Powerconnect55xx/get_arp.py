# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^vlan \d+\s+(?P<interface>\S+)\s+"
        r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface"),
            }]
        return r
