# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Iskratel.MBAN.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"Bridge mac address\s+: (?P<mac>\S+)")

    def execute(self):
        match = self.rx_mac.search(self.cli("show bridge status"))
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
