# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*(?P<ip>\d+\S+\d+)\s+(?P<mac>([0-9A-F]{2}-){5}[0-9A-F]{2})\s+", re.MULTILINE
    )

    def execute_cli(self, interface=None):
        r = []
        v = self.cli("show arp")
        for match in self.rx_line.finditer(v):
            r += [{"ip": match.group("ip"), "mac": match.group("mac")}]
        return r
