# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.HiFOCuS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "ECI.HiFOCuS.get_inventory"
    interface = IGetInventory

    def execute_cli(self, **kwargs):
        boards = self.profile.get_boards(self)
        r = []
        for board in boards:
            r += [
                {
                    "type": "LINECARD",
                    "number": board["slot"],
                    "vendor": "ECI",
                    "part_no": board["card_type"],
                    "serial": None,
                    "description": "",
                }
            ]
        return r
