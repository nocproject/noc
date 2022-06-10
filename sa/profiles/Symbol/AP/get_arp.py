# ---------------------------------------------------------------------
# Symbol.AP.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Symbol.AP.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+(?P<interface>vlan\d+)\s*",
        re.MULTILINE,
    )

    def execute_cli(self, vrf=None):
        r = []
        c = self.cli("show ip arp")
        for match in self.rx_line.finditer(c):
            r += [match.groupdict()]
        return r
