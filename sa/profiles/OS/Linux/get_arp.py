# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "OS.Linux.get_arp"
    implements = [IGetARP]

    rx_arp = re.compile(
        r"^\S+\s+\((?P<ip>\S+)\)\s+\S+\s+(?P<mac>\S+)\s+\S+\s+on+\s+(?P<interface>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_proc = re.compile(
        r"^(?P<ip>\S+)\s+0x1+\s+0x2+\s+(?P<mac>\S+)\s+\*+\s+(?P<interface>\S+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        for match in self.rx_arp.finditer(self.cli("arp -an")):
            r.append({
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface")
                    })
        if not r:
            for match in self.rx_proc.finditer(self.cli("cat /proc/net/arp")):
                r.append({
                        "ip": match.group("ip"),
                        "mac": match.group("mac"),
                        "interface": match.group("interface")
                        })
        if not r:
            raise Exception("Not implemented")
        return r
