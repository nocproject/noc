# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_arp"
    interface = IGetARP
    cache = True

    rx_line = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>\S+)\s+\d+\s+\S$",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("display arp")):
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r.append({
                    "ip": match.group("ip"),
                    "mac": None,
                    "interface": None
                    })
            else:
                r += [match.groupdict()]
        return r
