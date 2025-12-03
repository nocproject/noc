# ---------------------------------------------------------------------
# OS.FreeBSD.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "OS.FreeBSD.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^\S+\s+\((?P<ip>\S+)\)\s+\S+\s+(?P<mac>[0-9a-fA-F:]+)\s+\S+\s+(?P<interface>\S+)",
        re.MULTILINE | re.DOTALL,
    )

    def execute(self, vrf=None):
        s = self.cli("arp -an")
        return [
            {
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface"),
            }
            for match in self.rx_line.finditer(s)
            if match.group("mac") != "FF:FF:FF:FF:FF:FF"
        ]
