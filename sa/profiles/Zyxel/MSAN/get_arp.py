# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Zyxel.MSAN.get_arp"
    interface = IGetARP

    rx_arp1 = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+\d+\s+(?P<mac>\S+)\s+"
        r"(?P<interface>\S+).*\n", re.MULTILINE)
    rx_arp2 = re.compile(
        r"^(arp add ether\s+)?(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)(\s+#\s+\S+)?\s*\n", re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("ip arp show")
        except self.CLISyntaxError:
            v = self.cli("ip arp list")
        for match in self.rx_arp1.finditer(v):
            if match.group("interface") == "-":
                continue
            r += [match.groupdict()]
        if not r:
            for match in self.rx_arp2.finditer(v):
                r += [match.groupdict()]
        return r
