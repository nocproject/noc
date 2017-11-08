# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_chassis_id
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
    name = "Eltex.LTP.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s+MAC:\s+(?P<mac>\S+)\s*\n", re.MULTILINE)

    def execute(self):
        mac = self.cli("show system environment", cached=True)
        match = self.rx_mac.search(mac)
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
