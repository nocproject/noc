# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.text import parse_table


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_arp"
    interface = IGetARP

    def execute(self, interface=None):
        cmd = "show arp"
        if interface is not None:
            cmd += " interface %s" % interface
        v = self.cli(cmd)
        r = []
        t = parse_table(v)
        for i in t:
            r += [{"ip": i[0], "mac": i[1], "interface": i[2]}]
        return r
