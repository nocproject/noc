# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Orion.NOS.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.profile.get_version(self)
        return [{
            "type": "CHASSIS",
            "vendor": "Orion",
            "part_no": v["platform"],
            "revision": v["hardware"],
            "serial": v["serial"]
        }]
