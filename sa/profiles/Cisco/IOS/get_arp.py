# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re


class Script(noc.sa.script.Script):
    name = "Cisco.IOS.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"^Internet\s+(?P<ip>\S+)\s+\d+\s+(?P<mac>\S+)\s+\S+(?:\s+(?P<interface>\S+))")

    def execute(self, vrf=None):
        if vrf:
            s = self.cli("show ip arp vrf %s" % vrf)
        else:
            s = self.cli("show ip arp")
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
