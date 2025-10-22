# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Zhone.Bitstorm.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+\S+\s+(?P<interface>\S*)",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None):
        r = []
        try:
            v = self.cli("show management arp")
            for match in self.rx_line.finditer(v):
                iface = match.group("interface")
                if interface and interface != iface:
                    continue
                r += [{"interface": iface, "ip": match.group("ip"), "mac": match.group("mac")}]
        except self.CLISyntaxError:
            pass
        return r
