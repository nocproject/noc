# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Iskratel.MSAN.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Iskratel.MSAN.get_inventory"
    interface = IGetInventory

    def execute(self):
        v = self.profile.get_hardware(self)
        if "descr" in v:
            return [{
                "type": "LINECARD",
                "number": v["number"],
                "vendor": "ISKRATEL",
                "part_no": v["part_no"],
                "serial": v["serial"],
                "revision": v["hw_ver"],
                "description": v["descr"]
            }]
        else:
            return [{
                "type": "LINECARD",
                "number": v["number"],
                "vendor": "ISKRATEL",
                "part_no": v["part_no"],
                "serial": v["serial"]
            }]
