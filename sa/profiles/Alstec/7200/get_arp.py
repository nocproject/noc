# ---------------------------------------------------------------------
# Alstec.7200.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Alstec.7200.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<interface>\S+)\s*",
        re.MULTILINE,
    )

    def execute(self, interface=None):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp switch")):
            if (interface is not None) and (interface != match.group("interface")):
                continue
            r.append(match.groupdict())
        """
        cards = self.profile.fill_cards(self)
        for c in cards:
            if c["s"]:
                self.cli("join 0/%s" % c["n"])
                for match in self.rx_line.finditer(self.cli("show arp switch")):
                    mac = match.group("mac")
                    ip = match.group("ip")
                    found = False
                    for i in r:
                        if (i["ip"] == ip) and (i["mac"] == mac):
                            found = True
                            break
                    if not found:
                        r += [{
                            "mac": mac,
                            "ip": ip,
                            "interface": "1/%s" % match.group("interface")
                        }]
                self.cli("quit")
        """
        return r
