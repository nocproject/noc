# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_arp
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
    name = "DLink.DxS_Cisco_CLI.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^Internet\s+(?P<ip>\S+)\s+(\d+|\-\-)\s+(?P<mac>\S+)\s+arpa\s+"
        r"(?P<interface>.+)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface").strip()
                }]
        return r
