# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Terayon.BW.get_arp
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
    name = "Terayon.BW.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+N/A\s+(?P<interface>\S+)\s+dynamic",
        re.MULTILINE,
    )

    def execute(self, interface=None):
        r = []
        for match in self.rx_line.finditer(self.cli("show ip arp")):
            if interface is not None and interface != match.group("interface"):
                continue
            r += [match.groupdict()]
        return r
