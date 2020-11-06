# ---------------------------------------------------------------------
# Eltex.ESR.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_arp import Script as BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.ESR.get_arp"
    interface = IGetARP

    def execute_cli(self, interface=None):
        r = []
        c = self.cli("show arp")
        for iface, ip, mac, state, age in parse_table(c):
            if (interface is not None) and (interface != iface):
                continue
            if mac == "--":
                mac = None
            r += [{"ip": ip, "mac": mac, "interface": iface}]
        return r
