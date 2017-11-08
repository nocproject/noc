# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM.IOS.get_chassis_id
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
    name = "BDCOM.IOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"Base ethernet MAC Address: (?P<mac>\S+)")

    def execute(self):
        match = self.rx_mac.search(self.cli("show version", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
