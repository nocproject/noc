# ---------------------------------------------------------------------
# HP.ProCurve.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP

rx_line = re.compile(
    r"^\s*(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>[0-9a-f]{6}-[0-9a-f]{6})\s+(?:[Dd]ynamic|[Ss]tatic)\s+(?P<interface>\S+)"
)


class Script(BaseScript):
    name = "HP.ProCurve.get_arp"
    interface = IGetARP

    def execute(self):
        return self.cli("show arp", list_re=rx_line)
