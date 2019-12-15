# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSN.hiX56xx.get_arp
# sergey.sadovnikov@gmail.com
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
    name = "NSN.hiX56xx.get_arp"
    interface = IGetARP

    rx_arp = re.compile(
        r"^\s*(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\S+\s+(?P<interface>\S+)\s*\n", re.MULTILINE
    )

    def execute(self):
        r = []
        v = self.cli("show arp")
        for match in self.rx_arp.finditer(v):
            r += [match.groupdict()]
        return r
