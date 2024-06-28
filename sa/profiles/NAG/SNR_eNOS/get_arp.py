# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_arp import Script as BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_arp"
    interface = IGetARP
    cache = True

    rx_arp = re.compile(r"^(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+(?P<interface>\S+\d+)", re.MULTILINE)
    rx_arp2 = re.compile(
        r"^(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\d+\s+(?P<interface>\S+\d+)", re.MULTILINE
    )

    def execute_cli(self):
        if self.is_foxgate_cli:
            v = self.cli("show arp all")
            r = [match.groupdict() for match in self.rx_arp2.finditer(v)]
        else:
            v = self.cli("show arp")
            r = [match.groupdict() for match in self.rx_arp.finditer(v)]
        return r
