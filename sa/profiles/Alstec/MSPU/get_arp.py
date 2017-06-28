# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Alstec.MSPU.get_arp"
    interface = IGetARP
    cache = True

    rx_line = re.compile(
        r"^\? \((?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\) at "
        r"(?P<mac>\S+) \[ether\] on (?P<interface>\S+)", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        v = self.cli("context ip router arp show", cached=True)
        for match in self.rx_line.finditer(v):
            if (interface is not None) \
            and (interface != match.group("interface")):
                continue
            r.append(match.groupdict())
        return r
