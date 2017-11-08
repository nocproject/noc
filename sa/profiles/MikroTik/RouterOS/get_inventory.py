# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.scripts.get_version()
        platform = v["platform"]
        if platform not in ["x86", "CHR"]:
            return [{
                "type": "CHASSIS",
                "vendor": "MikroTik",
                "part_no": [platform],
                "serial": v["attributes"]["Serial Number"]
            }]
        return []
