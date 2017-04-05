# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.LTE.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.LTE.get_chassis_id"
    interface = IGetChassisID
    cache = True

    def execute(self):
        c = self.scripts.get_mac_address_table()
        for m in c:
            if m["type"] == "C":
                return {
                    "first_chassis_mac": m["mac"],
                    "last_chassis_mac": m["mac"]
                }
        return []
