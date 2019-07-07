# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_inventory"
    interface = IGetInventory

    def execute_cli(self):
        v = self.scripts.get_version()
        platform = v["platform"]
        if platform not in ["x86", "CHR"]:
            return [
                {
                    "type": "CHASSIS",
                    "vendor": "MikroTik",
                    "part_no": [platform],
                    "serial": v["attributes"]["Serial Number"],
                }
            ]
        return []
