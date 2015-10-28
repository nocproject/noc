# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Huawei.VRP.get_arp"
    interface = IGetARP

    rx_arp_line_vrp5 = re.compile(r"^(?P<ip>(\d+\.){3}\d+)\s+"
        r"(?P<mac>[0-9a-f\-]+)\s+\d*\s*.{3}\s+(?P<interface>\S+)",
        re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @BaseScript.match(version__startswith="5.")
    def execute_vrp5(self, vrf=None):
        if self.match_version(version__startswith="5.3"):
            displayarp = "display arp"
        else:
            if vrf:
                displayarp = "display arp vpn-instance %s" % vrf
            else:
                displayarp = "display arp all"
        return self.cli(displayarp, list_re=self.rx_arp_line_vrp5)

    rx_arp_line_vrp3 = re.compile(r"^\s*(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)"
        r"\s+(?P<vlan>\d+)\s+(?P<interface>\S+)\s+\d+\s+(?P<type>D|S)",
        re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @BaseScript.match()
    def execute_vrp3(self, vrf=None):
        arp = self.cli("display arp")
        return [{
            "ip": match.group("ip"),
            "interface": match.group("interface"),
            "mac": match.group("mac")
        } for match in self.rx_arp_line_vrp3.finditer(arp)]
