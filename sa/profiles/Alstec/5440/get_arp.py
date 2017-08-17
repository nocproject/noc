# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.5440.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Alstec.5440.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+0x1\s+0x\d+\s+"
        r"(?P<mac>\S+)\s+\S+\s+(?P<interfaces>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self, interface=None):
        r = []
        for match in self.rx_line.finditer(self.cli("arp show")):
            r += [match.groupdict()]
        return r
