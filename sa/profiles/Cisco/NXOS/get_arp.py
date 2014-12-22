# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.NXOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re


class Script(noc.sa.script.Script):
    name = "Cisco.NXOS.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"(?P<ip>([0-9]{1,3}\.){3}[0-9]{1,3})\s+\S+\s+(?P<mac>\S+)\s+(?P<interface>\S+)")

    def execute(self, vrf=None):
        if vrf:
            s = self.cli("show ip arp vrf %s | no-more" % vrf)
        else:
            s = self.cli("show ip arp all | no-more")
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r.append({"ip": match.group("ip"), "mac": None, "interface": None})
            else:
                r.append({"ip": match.group("ip"), "mac": match.group("mac"), "interface": match.group("interface")})
        return r
