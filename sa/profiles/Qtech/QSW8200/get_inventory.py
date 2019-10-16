# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Qtech.QSW8200.get_inventory"
    interface = IGetInventory

    def execute_cli(self):
        v = self.scripts.get_version()
        return [
            {
                "type": "CHASSIS",
                "vendor": "QTECH",
                "part_no": [v["platform"]],
                "revision": v["attributes"]["HW version"],
                "serial": v["attributes"]["Serial Number"],
            }
        ]
