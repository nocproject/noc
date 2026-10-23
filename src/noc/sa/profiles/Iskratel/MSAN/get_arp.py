# ---------------------------------------------------------------------
# Iskratel.MSAN.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Iskratel.MSAN.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_line2 = re.compile(
        r"^(?P<mac>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<interface>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute(self):
        r = []
        try:
            c = self.cli("show arp")
            for match in self.rx_line.finditer(c):
                r.append(match.groupdict())
        except self.CLISyntaxError:
            c = self.cli("show arp switch")
            for match in self.rx_line2.finditer(c):
                r.append(match.groupdict())
        return r
