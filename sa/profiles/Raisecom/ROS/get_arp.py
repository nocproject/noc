# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Raisecom.ROS.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+(\S+\s+)?"
        r"(?P<interface>\d+)(\s+dynamic\s+\d+)?\s*\n",
        re.MULTILINE,
    )

    rx_line1 = re.compile(
        r"^\s*(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+"
        r"(?P<interface>vlan?\d+)\s+\d+\s+dynamic\s+\d+\s+REACHABLE\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        v = self.cli("show arp")
        if not self.is_iscom2624g:
            for match in self.rx_line.finditer(v):
                r += [
                    {
                        "ip": match.group("ip"),
                        "mac": match.group("mac"),
                        "interface": "ip%s" % match.group("interface"),
                    }
                ]
        else:
            for match in self.rx_line1.finditer(v):
                r += [match.groupdict()]
        return r
