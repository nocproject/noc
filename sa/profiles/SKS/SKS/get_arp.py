# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_arp
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
    name = "SKS.SKS.get_arp"
    interface = IGetARP
    rx_line1 = re.compile(
        r"^vlan \d+\s+(?P<interface>\S+)\s+"
        r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+\S+\s*$",
        re.MULTILINE
    )
    rx_line2 = re.compile(
        r"^\s+IP\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?:\d+|-)\s+"
        r"(?P<mac>\S+)\s+\S+\s+(?P<interface>\S+?)(\(\S+\))?\s*\n",
        re.MULTILINE
    )

    def execute(self, interface=None):
        r = []
        c = self.cli("show arp")
        for match in self.rx_line1.finditer(c):
            if (
                interface is not None and
                interface != match.group("interface")
            ):
                continue
            r += [match.groupdict()]
        if not r:
            for match in self.rx_line2.finditer(c):
                if (
                    interface is not None and
                    interface != match.group("interface")
                ):
                    continue
                r += [match.groupdict()]
        return r
