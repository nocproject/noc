# ---------------------------------------------------------------------
# Iskratel.MBAN.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Iskratel.MBAN.get_inventory"
    interface = IGetInventory
    cache = True

    rx_inv1 = re.compile(
        r"^\s*(?P<number>\d+)\s+\S+\s+\S+\s+(?P<part_no>U\S+)\s+(?P<serial>[NZ]\S+)\s+",
        re.MULTILINE,
    )
    rx_inv2 = re.compile(
        r"^\s*(?P<number>\d+)\s+\S+\s+(?P<part_no>U\S+)\s+[UN]\S+\s+(?P<serial>[0-9A-Z\/]+)\s+",
        re.MULTILINE,
    )
    rx_cpu = re.compile(
        r"^\s*(?P<number>\d+)\s+\d+\s+CPU\S+\s+(?P<part_no>E\S+)\s+E\S+\s+"
        r"(?P<serial>[0-9A-Z]+)\s+",
        re.MULTILINE,
    )

    def execute(self):
        r = []
        c = self.cli("show board", cached=True)
        match = self.rx_inv1.search(c)
        if not match:
            match = self.rx_inv2.search(c)
        lc = {
            "type": "LINECARD",
            "number": match.group("number"),
            "vendor": "ISKRATEL",
            "part_no": match.group("part_no"),
        }
        if match.group("serial") != "N/A":
            lc["serial"] = match.group("serial")
        r += [lc]
        match = self.rx_cpu.search(c)
        if match:
            r += [
                {
                    "type": "CPU",
                    "number": match.group("number"),
                    "vendor": "ISKRATEL",
                    "part_no": match.group("part_no"),
                }
            ]
        return r
