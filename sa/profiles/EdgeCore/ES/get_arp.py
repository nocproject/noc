# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re


class Script(NOCScript):
    name = "EdgeCore.ES.get_arp"
    implements = [IGetARP]
    rx_line_4612 = re.compile(r"(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+\S+\s+(?P<interface>\d+)$", re.IGNORECASE | re.DOTALL | re.MULTILINE)
    rx_line = re.compile(r"^(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+(?P<interface>\S+)\s+", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match(platform__contains="4612")
    def execute_4612(self):
        #return self.cli("show arp",list_re=self.rx_line_4612)
        arp = self.cli("show arp")
        return [{"ip": match.group("ip"), "mac": match.group("mac"), "interface": "Vlan " + match.group("interface")} for match in self.rx_line_4612.finditer(arp)]

    @NOCScript.match()
    def execute_other(self):
        try:
            return self.cli("show arp", list_re=self.rx_line)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
