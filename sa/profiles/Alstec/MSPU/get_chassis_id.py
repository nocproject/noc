# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Alstec.MSPU.get_chassis_id"
    interface = IGetChassisID
    cache = True

    def execute(self):
        r = []
        v = self.scripts.get_mac_address_table()
        for i in v:
            if i["type"] == "C":
                r += [{
                    "first_chassis_mac": i["mac"],
                    "last_chassis_mac": i["mac"]
                }]
        return r
