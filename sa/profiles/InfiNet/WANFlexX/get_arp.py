# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InfiNet.WANFlexX.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "InfiNet.WANFlexX.get_arp"
    implements = [IGetARP]
    rx_arp = re.compile(r"^(?P<ip>\S+)\s+at\s+(?P<mac>[0-9a-f]+)\s+via\s+"
                        r"(?P<interface>\S+)$", re.MULTILINE)

    def execute(self):
        arp = self.cli("arp view")
        r = []
        for match in self.rx_arp.finditer(arp):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
