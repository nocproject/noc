# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.ALS.get_chassis_id
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
    name = "Alstec.ALS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self):
        match = self.rx_mac.search(self.cli("show system", cached=True))
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
