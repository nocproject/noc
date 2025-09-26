# ---------------------------------------------------------------------
# Brocade.IronWare.get_arp
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
    name = "Brocade.IronWare.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^\d+\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\d+\s+(?P<interface>\S+)"
    )

    def execute_cli(self):
        s = self.cli("show arp")
        r = []
        for match in self.rx_line.finditer(s):
            type = match.group("type")
            mac = match.group("mac")
            if mac.lower() in ("incomplete" or "none") or type.lower() in ("pending", "invalid"):
                continue
            r += [
                {
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface"),
                }
            ]
        return r
