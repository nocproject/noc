# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Qtech.QSW2800.get_arp"
    interface = IGetARP

    rx_line = re.compile(r"^(?P<ip>\S+)\s+(?P<mac>[0-9a-f\-]+)\s+\S+\s+"
                        r"(?P<iface>\S+)\s+\S+\s+\d+", re.MULTILINE)

    def execute(self):
        r = []
        cmd = self.cli("show arp")
        for match in self.rx_line.finditer(cmd):
            r += [{
                "ip": match.group("ip"),
                "mac": match.group("mac"),
                "interface": match.group("iface")
            }]
        return r
