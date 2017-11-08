# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_inventory
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
    name = "Huawei.MA5600T.get_inventory"
    interface = IGetInventory

    rx_slot = re.compile(
        r"^\s*Pcb\s+Version\s*:\s+(?P<part_no>\S+)\s+"
        r"VER (?P<revision>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE)
    rx_sub = re.compile(
        r"^\s*(VOIP)?SubBoard(\[(?P<number>\d+)\])?:\s*\n"
        r"^\s*Pcb\s+Version\s*:\s+(?P<part_no>\S+)\s+"
        r"VER (?P<revision>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        r = []
        v = self.scripts.get_version()
        platform = v["platform"]
        r += [{
            "type": "CHASSIS",
            "vendor": "HUAWEI",
            "part_no": platform,
        }]
        for i in range(self.profile.get_slots_n(self) + 1):
            v = self.cli("display version 0/%d" % i)
            match = self.rx_slot.search(v)
            if match:
                r += [{
                    "type": "LINECARD",
                    "number": i,
                    "vendor": "HUAWEI",
                    "part_no": match.group("part_no"),
                    "revision": match.group("revision")
                }]
            for match in self.rx_sub.finditer(v):
                r += [{
                    "type": "SUB",
                    "number": int(match.group("number") or 0),
                    "vendor": "HUAWEI",
                    "part_no": match.group("part_no"),
                    "revision": match.group("revision")
                }]
        return r
