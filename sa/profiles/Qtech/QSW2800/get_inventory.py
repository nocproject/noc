# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Qtech.QSW2800.get_inventory"
    interface = IGetInventory

    def execute(self):
        r = {"type": "CHASSIS",
             "number": "1",
             "vendor": "QTECH",
             }
        v = self.scripts.get_version()
        if "part_no" not in v:
            return []
        r.update({
            "part_no": [v["platform"]],
            "revision": v["attributes"]["HW version"],
            "serial": v["attributes"]["Serial Number"]
        })
        return [r]
