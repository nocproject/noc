# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "TPLink.T2600G.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"Mac Address\s+- (?P<mac>.+)$", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show system-info", cached=True)
        match = self.rx_mac.search(v)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
