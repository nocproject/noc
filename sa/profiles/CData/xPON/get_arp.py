# ---------------------------------------------------------------------
# CData.xPON.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "CData.xPON.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>[xgpl]\S+\d)\s+\S+\s+\d+\s*\n",
        re.MULTILINE,
    )
    rx_line2 = re.compile(
        r"^(?P<ip>\S+)\s+(?P<mac>\S+)\s+\d+\s+s\s+\S+\s+\d+\s+(?P<interface>[xgpl]\S+\d)\s+.+\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        with self.configure():
            try:
                v = self.cli("show arp all")
                for match in self.rx_line.finditer(v):
                    r += [match.groupdict()]
            except self.CLISyntaxError:
                v = self.cli("show arp entry all")
                for match in self.rx_line2.finditer(v):
                    r += [match.groupdict()]
        return r
