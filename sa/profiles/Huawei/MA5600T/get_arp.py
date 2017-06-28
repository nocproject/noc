# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Huawei.MA5600T.get_arp"
    interface = IGetARP

    rx_arp1 = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+"
        r"(?P<vlan>\d+)\s+(?P<interface>\d+\s*/\d+\s*/\d+\s*).*\n",
        re.MULTILINE)
    rx_arp2 = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s*\n",
        re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("display arp all\n")
        for match in self.rx_arp1.finditer(v):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("interface").replace(" ", "")
            }]
        if not r:
            for match in self.rx_arp2.finditer(v):
                r += [match.groupdict()]
        return r
