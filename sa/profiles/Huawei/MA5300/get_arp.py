# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_arp
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

"""
"""

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Huawei.MA5300.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+(?P<vlan>\d+)\s+(?P<interface>\S+)\s+(?P<type>\S+)$")

    def execute(self):
        s = self.cli("show arp all")
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            r.append({
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface")
            })
        return r
