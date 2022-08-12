# ---------------------------------------------------------------------
# Mellanox.Cumulus.get_arp
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
    name = "Mellanox.Cumulus.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>\S+)\s+ether\s+(?P<mac>\S+)\s+\S+\s+(?P<interface>\S+)\s*\n", re.MULTILINE
    )

    def execute_cli(self):
        r = []
        v = self.cli("arp -n")
        for match in self.rx_line.finditer(v):
            r += [match.groupdict()]
        return r
