# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*(?:vlan \d+\s+)?(?P<interface>g?e?\d\S*)\s+(?P<ip>\d\S+)\s+"
        r"(?P<mac>\S+)\s+(?:[Dd]ynamic|[Ss]tatic)", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            }]
        return r
