# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Intracom.UltraLink.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Intracom.UltraLink.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"(?:MAC|mac)\s?[Aa]ddress : (?P<mac>\S+)")

    def execute_cli(self, **kwargs):
        macs = []
        cli = self.cli("get system mng")
        for match in self.rx_mac.finditer(cli):
            macs += [match.group("mac")]
        cli = self.cli("get ethernet state")
        for match in self.rx_mac.finditer(cli):
            macs += [match.group("mac")]

        return [
            {"first_chassis_mac": fmac, "last_chassis_mac": lmac}
            for fmac, lmac in self.macs_to_ranges(macs)
        ]
