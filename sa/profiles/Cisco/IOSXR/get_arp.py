# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_arp
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
    name = "Cisco.IOSXR.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"(?P<ip>\S+)\s+\S+\s+"
                         r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
                         r"Dynamic\s+"
                         r"ARPA\s+"
                         r"(?P<interface>\S+)", re.IGNORECASE)

    def execute(self, vrf=None):
        if vrf:
            s = self.cli("show arp table %s" % vrf)
        else:
            s = self.cli("show arp")
        r = {}  # ip -> (mac, interface)
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            r[match.group("ip")] = (match.group("mac"), match.group("interface"))
        return [{"ip": k, "mac": r[k][0], "interface": r[k][1]} for k in r]
