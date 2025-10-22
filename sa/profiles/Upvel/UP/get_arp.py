# ---------------------------------------------------------------------
# Upvel.UP.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Pyton modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Upvel.UP.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+via\s+(?P<interface>\S+):(?P<mac>\S+)\s*$",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None):
        r = []
        v = self.cli("show ip arp")
        for match in self.rx_line.finditer(v):
            if (interface is not None) and interface != match.group("interface"):
                continue
            r += [match.groupdict()]
        return r
