# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript
import re


class Script(noc.sa.script.Script):
    name = "Huawei.VRP.get_arp"
    implements = [IGetARP]

    rx_arp_line_vrp5 = re.compile(r"^(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+\d*\s+.{3}\s+(?P<interface>\S+)", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match(version__startswith="5.")
    def execute_vrp5(self):
        return self.cli("display arp all", list_re=self.rx_arp_line_vrp5)

    rx_arp_line_vrp3 = re.compile(r"^\s*(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+(?P<vlan>\d+)\s+(?P<interface>\S+)\s+\d+\s+(?P<type>D|S)", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match()
    def execute_vrp3(self):
        arp = self.cli("display arp")
        return [{
            "ip": match.group("ip"),
            "interface": match.group("interface"),
            "mac": match.group("mac")
        } for match in self.rx_arp_line_vrp3.finditer(arp)]
