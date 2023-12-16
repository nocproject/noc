# ---------------------------------------------------------------------
# HP.Aruba.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.sa.profiles.Generic.get_arp import Script as BaseScript


class Script(BaseScript):
    name = "HP.Aruba.get_arp"
    interface = IGetARP
    rx_arp_table = re.compile(
        r"(?P<address>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+"
        r"(?P<port>\S+)\s+(?P<pprot>\d+/\d+/\d+|lag\d+)"
    )

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show arp")
        for ip, mac, vlan, port in self.rx_arp_table.findall(v):
            r += [
                {
                    "ip": ip,
                    "mac": mac,
                    "interface": port,
                }
            ]
        return r
