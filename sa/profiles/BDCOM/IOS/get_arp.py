# ---------------------------------------------------------------------
# BDCOM.IOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "BDCOM.IOS.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"IP\s+(?P<ip>\S+)\s+(?:\-|\d+)\s+(?P<mac>\S+)\s+ARPA\s+(?P<interface>\S+)"
    )

    def execute(self, vrf=None):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            if "(" in match.group("interface"):
                svi, phys = match.group("interface").split("(")
                r += [
                    {
                        "ip": match.group("ip"),
                        "mac": match.group("mac"),
                        "interface": self.profile.convert_interface_name(svi),
                    }
                ]
            else:
                r += [match.groupdict()]
        return r
