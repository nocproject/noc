# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Alstec.MSPU.get_inventory"
    cache = True
    interface = IGetInventory

    def execute_cli(self):
        v = self.scripts.get_version()
        r = {"type": "CHASSIS", "vendor": "ALSTEC", "part_no": v["platform"]}
        if "HW version" in v["attributes"]:
            r["revision"] = v["attributes"]["HW version"]
        if "Serial Number" in v["attributes"]:
            r["serial"] = v["attributes"]["Serial Number"]
        return [r]
