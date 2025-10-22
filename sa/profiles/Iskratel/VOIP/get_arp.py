# ---------------------------------------------------------------------
# Iskratel.VOIP.get_arp
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
    name = "Iskratel.VOIP.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+\S+\s*\n", re.MULTILINE
    )

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show arp")):
            r += [match.groupdict()]
        return r
