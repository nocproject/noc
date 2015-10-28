# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_arp"
    interface = IGetARP
    rx_arp = re.compile(r"^\s+\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+"
                        r"(?P<interface>\d+).*$",
                        re.MULTILINE)

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
