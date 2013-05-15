# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "Arista.EOS.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(
        r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"\d+\s+"
        r"(?P<mac>\S+)\s+"
        r"(?P<interfaces>.+)$"
    )

    def execute(self, vrf=None):
        s = self.cli("show arp")
        r = []
        for l in s.splitlines():
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            ifaces = match.group("interfaces")
            if "not learned" in ifaces:
                continue
            if ifaces.startswith("Vlan"):
                iface = ifaces.split(",", 1)[0]
            else:
                iface = ifaces
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": iface
            }]
        return r
