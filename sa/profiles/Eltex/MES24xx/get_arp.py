# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES24xx.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES24xx.get_arp"
    interface = IGetARP

    def execute(self, interface=None):
        r = []
        for i in parse_table(self.cli("show ip arp"), expand_columns=True):
            if interface is not None and interface != i[3]:
                continue
            r += [{"ip": i[0], "mac": i[1], "interface": i[3]}]
        return r
