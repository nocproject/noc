# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QOS.get_chassis_id
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
    name = "Qtech.QOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^System MacAddress: (?P<mac>\S+)\s*\n", re.MULTILINE)

    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.rx_mac.search(ver)
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
