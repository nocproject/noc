# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Brocade.IronWare.get_arp"
    interface = IGetARP
    rx_line = re.compile(r"^\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\d+\s+(?P<interface>\S+)")

    def execute(self):
        s = self.cli("show arp")
        r = []
        for l in s.splitlines():
            match = rx_line.match(l.strip())
            if not match:
                continue
            type = match.group("type")
            mac = match.group("mac")
            if (mac.lower() in ("incomplete" or "none") or
                type.lower() in ("pending", "invalid")):
                continue
            else:
                r += [{
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface")
                }]
        return r
