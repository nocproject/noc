# ---------------------------------------------------------------------
# DLink.DxS.get_arp
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
    name = "DLink.DxS.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^(?P<interface>\S*)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+\S+\s*$",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None):
        r = []
        iface_old = ""
        for match in self.rx_line.finditer(self.cli("show arpentry")):
            mac = match.group("mac")
            if mac == "FF-FF-FF-FF-FF-FF":
                continue
            iface = match.group("interface")
            if not iface:
                # DES-1210-28/ME B2 with firmware 6.09.B047 can hide
                # interface name in some rare cases
                iface = iface_old
            else:
                iface_old = iface
            if (interface is not None) and (interface != iface):
                continue
            r += [{"interface": iface, "ip": match.group("ip"), "mac": mac}]
        return r
