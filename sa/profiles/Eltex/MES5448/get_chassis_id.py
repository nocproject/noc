# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Eltex.MES5448.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Eltex.MES5448.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self):
        match = self.rx_mac.search(self.cli("show version", cached=True))
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
