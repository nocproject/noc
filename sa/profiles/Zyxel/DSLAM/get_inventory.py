# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.DSLAM.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Zyxel.DSLAM.get_inventory"
    interface = IGetInventory

    rx_hw = re.compile(
        r"^\s*Model\s*:\s+\S+ / (?P<part_no>\S+)\s*\n"
        r"^.+?\n"
        r"^\s*Hardware version\s*:\s+(?P<revision>\S+)\s*\n"
        r"^\s*Serial number\s*:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.rx_hw.search(self.cli("sys info show"))
        return [{
            "type": "CHASSIS",
            "vendor": "ZYXEL",
            "part_no": match.group("part_no"),
            "serial": match.group("serial"),
            "revision": match.group("revision")
        }]
