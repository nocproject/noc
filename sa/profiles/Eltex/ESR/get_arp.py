# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Eltex.ESR.get_arp"
    interface = IGetARP

    def execute(self, interface=None):
        r = []
        c = self.cli("show arp")
        for iface, ip, mac, state, age in parse_table(c):
            if (interface is not None) and (interface != iface):
                continue
            if mac == "--":
                mac = None
            r += [{
                "ip": ip,
                "mac": mac,
                "interface": iface
            }]
        return r
