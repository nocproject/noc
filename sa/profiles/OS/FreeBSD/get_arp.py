# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(
    r"^\S+\s+\((?P<ip>\S+)\)\s+\S+\s+(?P<mac>\S+)\s+\S+\s+(?P<interface>\S+)",
     re.MULTILINE | re.DOTALL)

    def execute(self, vrf=None):
        if vrf:
            s = self.cli("setfib %d arp -an" % vrf)
        else:
            s = self.cli("arp -an")
        r = []
        for match in self.rx_line.finditer(s):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
