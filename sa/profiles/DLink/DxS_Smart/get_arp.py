# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_arp
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
    name = "DLink.DxS_Smart.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+ARPA\s+(?P<interface>\S+)\s+\S+", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("debug info")):
            r += [{
                "ip":match.group("ip"),
                "mac":match.group("mac"),
                "interface":match.group("interface"),
            }]
        return r
