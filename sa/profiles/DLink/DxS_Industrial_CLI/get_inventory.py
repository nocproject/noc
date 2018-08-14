# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.scripts.get_version()
        p = {
            "type": "CHASSIS",
            "vendor": "DLINK",
            "part_no": [v["platform"]],
            "revision": v["attributes"]["HW version"]
        }
        if "Serial Number" in v["attributes"]:
            p["serial"] = v["attributes"]["Serial Number"]
        return [p]
