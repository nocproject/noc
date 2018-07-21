# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Zhone.Bitstorm.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+"
        r"\S+\s+(?P<interface>\S*)",
        re.MULTILINE
    )

    def execute(self, interface=None):
        r = []
        v = self.cli("show management arp")
        for match in self.rx_line.finditer(v):
            iface = match.group("interface")
            if interface and interface != iface:
                continue
            r += [{
                "interface": iface,
                "ip": match.group("ip"),
                "mac": match.group("mac")
            }]
        return r
