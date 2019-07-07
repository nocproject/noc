# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Eltex.LTP.get_inventory"
    interface = IGetInventory
    cache = True

    rx_platform = re.compile(
        r"^\s*TYPE:\s+(?P<part_no>\S+)\s*\n"
        r"^\s*HW_revision:\s+(?P<revision>\S+)\s*\n"
        r"^\s*SN:\s+(?P<serial>\S+)",
        re.MULTILINE,
    )
    rx_pwr = re.compile(r"^\s*Module (?P<num>\d+): (?P<part_no>PM\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("show system environment", cached=True)
        match = self.rx_platform.search(v)

        r = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": match.group("part_no"),
                "serial": match.group("serial"),
                "revision": match.group("revision"),
            }
        ]

        for match in self.rx_pwr.finditer(v):
            r += [
                {
                    "type": "PWR",
                    "vendor": "ELTEX",
                    "part_no": match.group("part_no"),
                    "number": match.group("num"),
                }
            ]

        return r
