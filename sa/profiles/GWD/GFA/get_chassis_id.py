# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GWD.GFA.get_chassis_id
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
    name = "GWD.GFA.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^Sysmac : (?P<mac>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
