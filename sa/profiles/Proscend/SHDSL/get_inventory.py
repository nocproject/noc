# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Proscend.SHDSL.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Proscend.SHDSL.get_inventory"
    interface = IGetInventory

    def execute_snmp(self):
        v = self.scripts.get_version()
        return [
            {
                "type": "CHASSIS",
                "vendor": "Proscend",
                "part_no": [v["platform"]],
                "serial": v["attributes"]["Serial Number"],
            }
        ]
