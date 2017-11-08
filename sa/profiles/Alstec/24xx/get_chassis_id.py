# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Alstec.24xx.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s*(MAC Address|Burned In MAC Address)\s*\.+ (?P<mac>\S+)\s*.+", re.MULTILINE)

    def execute(self):
        match = self.rx_mac.search(self.cli("show network", cached=True))
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
