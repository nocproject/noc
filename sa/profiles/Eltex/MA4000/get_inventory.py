# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_inventory"
    interface = IGetInventory

    rx_slot = re.compile(
        r"^\s*Module type:\s+(?P<part_no>\S+)\s*\n"
        r"^\s*Hardware version:\s+(?P<revision>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        v = self.scripts.get_version()
        res = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": v["platform"],
                "serial": v["attributes"]["Serial Number"],
            }
        ]

        v = self.cli("show shelf")
        for i in parse_table(v):
            if i[2] == "none":
                continue
            c = self.cli("show slot %s information" % i[0])
            match = self.rx_slot.search(c)
            r = {
                "type": "LINECARD",
                "number": i[0],
                "vendor": "ELTEX",
                "serial": i[4],
                "part_no": match.group("part_no"),
                "revision": match.group("revision"),
            }
            res += [r]

        return res
