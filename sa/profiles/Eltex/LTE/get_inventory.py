# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Eltex.LTE.get_inventory"
    interface = IGetInventory
    cache = True

    def execute_cli(self):
        v = self.scripts.get_version()
        p = {
            "type": "CHASSIS",
            "vendor": "ELTEX",
            "part_no": v["platform"],
        }
        if v.get("attributes", {}).get("Serial Number", ""):
            p["serial"] = v["attributes"]["Serial Number"]

        return [p]
