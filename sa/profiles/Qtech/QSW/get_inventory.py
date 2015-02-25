# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(NOCScript):
    name = "Qtech.QSW.get_inventory"
    implements = [IGetInventory]

    def execute(self):
        v = self.scripts.get_version()
        return [{
            "type": "CHASSIS",
            "number": "1",
            "vendor": "QTECH",
            "part_no": [v["platform"]],
            "revision": v["attributes"]["HW version"],
            "serial": v["attributes"]["Serial Number"]
        }]
