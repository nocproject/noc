# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TPLink.T2600G.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "TPLink.T2600G.get_arp"
    interface = IGetARP

    rx_line = re.compile(r"^(?P<iface>\S+)\s+(?P<ip>[0-9\.]+)\s+(?P<mac>[0-9a-f\:]+)", re.MULTILINE)

    def execute_cli(self):
        r = []
        cmd = self.cli("show arp")
        for match in self.rx_line.finditer(cmd):
            r += [
                {
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("iface"),
                }
            ]
        return r
