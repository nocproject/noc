# ---------------------------------------------------------------------
# Vitesse.VSC.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Vitesse.VSC.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+via\s+(?P<interface>(VLAN )?\S+):(?P<mac>\S+)",
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
