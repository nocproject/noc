# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.OS62xx.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re

rx_line = re.compile(
    r"^\s*(?P<interface>\d\S+)\s+(?P<ip>\d\S+)\s+(?P<mac>\S+)\s+(?:Dynamic|Static)", re.MULTILINE)


class Script(NOCScript):
    name = "Alcatel.OS62xx.get_arp"
    implements = [IGetARP]

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
