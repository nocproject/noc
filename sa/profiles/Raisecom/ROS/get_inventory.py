# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_inventory
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
    name = "Raisecom.ROS.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.profile.get_version(self)
        return [{
            "type": "CHASSIS",
            "number": "1",
            "vendor": "RAISECOM",
            "part_no": v["platform"],
            "revision": v["hw_rev"],
            "serial": v["serial"]
        }]
