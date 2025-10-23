# ---------------------------------------------------------------------
# Eltex.LTP.get_arp
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
    name = "Eltex.LTP.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*\d+\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+(?P<interface>\S+ \d+)\s+", re.MULTILINE
    )

    def execute(self):
        r = []
        with self.profile.switch(self):
            arp = self.cli("show ip arp table")
            for match in self.rx_line.finditer(arp):
                r += [match.groupdict()]
        return r
