# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GWD.GFA.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "GWD.GFA.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\d+\s+\S+\s+\d+\s+(?P<interface>\S+)\s*\n", re.MULTILINE
    )

    def execute_cli(self, vrf=None):
        r = []
        v = self.cli("show arp")
        for match in self.rx_line.finditer(v):
            r += [match.groupdict()]
        return r
