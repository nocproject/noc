# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_arp
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
    name = "Cisco.IOSXR.get_arp"
    implements = [IGetARP]
    rx_line = re.compile(r"(?P<ip>\S+)\s+\S+\s+"
                         r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
                         r"Dynamic\s+"
                         r"ARPA\s+"
                         r"(?P<interface>\S+)", re.IGNORECASE)

    def execute(self, vrf=None):
        if vrf:
            try:
                s = self.cli("show arp vrf %s" % vrf)
            except self.CLISyntaxError:
                s = self.cli("show arp table %s" % vrf)
        else:
            s = self.cli("show arp")
        r = {}  # ip -> (mac, interface)
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            r[match.group("ip")] = (
                match.group("mac"), match.group("interface")
            )
        return [{"ip": k, "mac": r[k][0], "interface": r[k][1]} for k in r]
