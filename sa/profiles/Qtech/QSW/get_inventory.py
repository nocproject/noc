# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
 
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


<<<<<<< HEAD
class Script(BaseScript):
    name = "Qtech.QSW.get_inventory"
    interface = IGetInventory
=======
class Script(NOCScript):
    name = "Qtech.QSW.get_inventory"
    implements = [IGetInventory]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
