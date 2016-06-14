# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.MSAN.get_arp"
    interface = IGetARP

    rx_arp = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+\d+\s+(?P<mac>\S+)\s+"
        r"(?P<interface>\S+).*$", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_arp.finditer(self.cli("show arp")):
            r.append(match.groupdict())
        return r
