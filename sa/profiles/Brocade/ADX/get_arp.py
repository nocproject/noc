# ---------------------------------------------------------------------
# Brocade.ADX.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Brocade.ADX.get_arp"
    interface = IGetARP

    rx_line = re.compile(r"^\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+\S+\s+\d+(?:\s+(?P<interface>\S+))")

    def execute(self, vrf=None):
        s = self.cli("show arp")
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r += [{"ip": match.group("ip"), "mac": None, "interface": None}]
            else:
                r += [
                    {
                        "ip": match.group("ip"),
                        "mac": match.group("mac"),
                        "interface": match.group("interface"),
                    }
                ]
        return r
