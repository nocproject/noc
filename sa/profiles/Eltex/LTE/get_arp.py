# ---------------------------------------------------------------------
# Eltex.LTE.get_arp
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
    name = "Eltex.LTE.get_arp"
    interface = IGetARP
    cache = True

    rx_line = re.compile(
        r"^\s*\d+\s+port\s+(?P<interface>\d+)\s+(?P<mac>\S+)\s+(?P<ip>\d+\S+)", re.MULTILINE
    )
    rx_line2 = re.compile(
        r"^\s*(?P<vlan>\d+)\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+(?P<interface>\S+\s\d+)\s+",
        re.MULTILINE,
    )

    def execute(self):
        r = []
        with self.profile.switch(self):
            try:
                arp = self.cli("show arp", cached=True)
                for match in self.rx_line.finditer(arp):
                    if match.group("mac") == "00:00:00:00:00:00":
                        r += [{"ip": match.group("ip"), "mac": None, "interface": None}]
                    else:
                        r += [match.groupdict()]
            except self.CLISyntaxError:
                arp = self.cli("show ip arp table", cached=True)
                for match in self.rx_line2.finditer(arp):
                    if match.group("mac") == "00:00:00:00:00:00":
                        r += [{"ip": match.group("ip"), "mac": None, "interface": None}]
                    else:
                        r += [match.groupdict()]
        return r
