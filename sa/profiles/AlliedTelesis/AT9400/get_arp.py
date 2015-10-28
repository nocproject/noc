# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9400.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT9400.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^\S+\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s*",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show ip arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface"),
            }]
        return r
