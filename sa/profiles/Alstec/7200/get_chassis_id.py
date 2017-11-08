# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.get_chassis_id
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
    name = "Alstec.7200.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^Burned In MAC Address\.+ (?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        match = self.rx_mac.search(self.cli("show version", cached=True))
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
