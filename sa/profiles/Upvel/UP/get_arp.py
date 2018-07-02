# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UPVEL.UP.get_arp
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
    name = "UPVEL.UP.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+via\s+(?P<interface>\S+):"
        r"(?P<mac>\S+)\s*$", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        v = self.cli("show ip arp")
        for match in self.rx_line.finditer(v):
            if (
                (interface is not None) and
                interface != match.group("interface")
            ):
                continue
            r += [match.groupdict()]
        return r
