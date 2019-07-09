# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Polygon.IOS.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Polygon.IOS.get_arp"
    cache = True
    interface = IGetARP

    rx_line = re.compile(r"^(?P<ip>\d\S+)\s+(?:\S+)\s+(?P<mac>\S+)\s(?P<interface>\S+)")

    def execute_cli(self, vrf=None):
        if vrf:
            s = self.cli("show ip arp vrf %s" % vrf)
        else:
            s = self.cli("show arp")
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r.append({"ip": match.group("ip"), "mac": None, "interface": None})
            else:
                r.append(
                    {
                        "ip": match.group("ip"),
                        "mac": match.group("mac"),
                        "interface": match.group("interface"),
                    }
                )
        return r
