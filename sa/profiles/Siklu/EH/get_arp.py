# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Siklu.EH.get_arp"
    interface = IGetARP

    def execute(self):
        v = self.cli("show arp")
        r = []
        for l in v.splitlines():
            parts = l.split()
            if len(parts) == 3 and parts[2] == "dynamic":
                r += [{
                    "ip": parts[0],
                    "mac": parts[1]
                }]
        return r
