# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Qtech.QSW8200.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"System MAC Address: (?P<mac>\S+)")

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_mac.search(v)
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
