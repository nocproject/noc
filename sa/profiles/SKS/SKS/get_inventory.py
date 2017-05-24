# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_inventory
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
    name = "SKS.SKS.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.scripts.get_version()
        r = {
            "type": "CHASSIS",
            "vendor": "SKS",
            "part_no": v["platform"],
            "revision": v["attributes"]["HW version"]
        }
        if "Serial Number" in v["attributes"]:
            r["serial"] =  v["attributes"]["Serial Number"]
        return [r]
