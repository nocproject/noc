# ---------------------------------------------------------------------
# VyOS.VyOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_arp import Script as BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.text import parse_table


class Script(BaseScript):
    name = "VyOS.VyOS.get_arp"
    interface = IGetARP
    always_prefer = "S"

    def execute_cli(self, interface=None):
        cmd = "show arp"
        if interface is not None:
            cmd += f"interface {interface}"
        v = self.cli(cmd)
        r = []
        t = parse_table(v)
        for i in t:
            if i[2] != "":
                r.append({"ip": i[0], "mac": i[2], "interface": i[1]})
        return r
