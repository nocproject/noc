# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_arp"
    implements = [IGetARP]
    rx_arp = re.compile(r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\S+\s+\d+\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>\S+)", re.MULTILINE)

    def execute(self):
        arp = self.cli("ip arp status")
        r = []
        for match in self.rx_arp.finditer(arp):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
