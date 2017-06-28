# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "3Com.SuperStack3.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.profile.get_hardware(self)
        return [{
            "type": "CHASSIS",
            "vendor": "3COM",
            "part_no": v["part_no"],
            "revision": v["hardware"],
            "serial": v["serial"]
        }]
