# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Qtech.QSW8200.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>[0-9\.]+)\s+(?P<mac>[0-9A-F\.]+)\s+(?P<iface>\S+)",
        re.MULTILINE
    )

    def execute(self):
        r = []
        cmd = self.cli("show arp")
        for match in self.rx_line.finditer(cmd):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("iface")
            }]
        return r
