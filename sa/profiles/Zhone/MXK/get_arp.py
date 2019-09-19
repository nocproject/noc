# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.MXK.get_arp
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
    name = "Zhone.MXK.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>\d\S+)\s+(?P<mac>\S+)\s+\d+\s+\d+\s+\d+\s+(?P<interface>\S+)\s*\n", re.MULTILINE
    )

    def execute(self, vrf=None):
        r = []
        for match in self.rx_line.finditer(self.cli("ip arpshow")):
            if match.group("mac") == "<incomplete>" or match.group("interface") == "coreEnd":
                continue
            r += [match.groupdict()]
        return r
