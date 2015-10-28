# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.OS62xx.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re

rx_line = re.compile(
    r"^\s*(?P<interface>\d\S+)\s+(?P<ip>\d\S+)\s+(?P<mac>\S+)\s+(?:Dynamic|Static)", re.MULTILINE)


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_arp"
    interface = IGetARP

    def execute(self):
        r = []
        for match in rx_line.finditer(self.cli("show arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
