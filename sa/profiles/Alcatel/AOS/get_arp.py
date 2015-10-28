# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_arp
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
    r"^\s*(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\S+\s+(?:P|A|V){,3}\s+"
    r"(?P<interface>\d\S+)", re.MULTILINE)


class Script(BaseScript):
    name = "Alcatel.AOS.get_arp"
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
