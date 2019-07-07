# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.Summit200.get_chassis_id
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
    name = "Extreme.Summit200.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^System MAC:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show switch", cached=True)
        match = self.rx_mac.search(v)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
