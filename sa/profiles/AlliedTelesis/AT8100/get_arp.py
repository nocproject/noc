# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "AlliedTelesis.AT8100.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<interface>vlan\d+)\s+"
        r"(?P<port>port\d\S+)\s+\S+\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show arp")
        r = []
        for match in self.rx_line.finditer(v):
            r += [
                {
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface"),
                }
            ]
        return r
