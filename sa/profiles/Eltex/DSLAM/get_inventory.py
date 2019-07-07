# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.DSLAM.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Eltex.DSLAM.get_inventory"
    interface = IGetInventory

    def execute_cli(self, **kwargs):
        v = self.scripts.get_version()
        return [{"type": "CHASSIS", "vendor": "ELTEX", "part_no": v["platform"]}]
