# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_arp"
    implements = [IGetARP]
    rx_arp = re.compile(r"^\s+\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<interface>\d+).*$", re.MULTILINE)

    def execute(self):
        arp = self.cli("show ip arp")
        r = []
        for match in self.rx_arp.finditer(arp):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
