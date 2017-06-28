# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_inventory
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
    name = "Iskratel.MSAN.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.profile.get_hardware(self)
        r = {
            "vendor": "ISKRATEL",
            "part_no": v["part_no"],
            "serial": v["serial"]
        }
        if v["number"]:
            r["type"] = "LINECARD"
            r["number"] = v["number"]
        else:
            r["type"] = "CHASSIS"
        if "descr" in v:
            r["description"] = v["descr"]
        if "revision" in v:
            r["revision"] = v["hw_ver"]

        # TODO: use `show slot` command

        return [r]
