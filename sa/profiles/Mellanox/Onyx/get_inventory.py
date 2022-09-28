# ---------------------------------------------------------------------
# Mellanox.Onyx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Mellanox.Onyx.get_inventory"
    interface = IGetInventory

    rx_trans = re.compile(
        r"^Port 1/(?P<number>\d+) state\s*\n"
        r"^\s+identifier\s+: \S+\s*\n"
        r"^\s+cable/module type\s+: .+\n"
        r"^\s+ethernet speed and type: .+\n"
        r"^\s+vendor\s+: (?P<vendor>.+)\n"
        r"^\s+(?:supported )?cable length\s+: .+\n"
        r"^\s+part number\s+: (?P<part_no>\S+)\s*\n"
        r"^\s+revision\s+: (?P<revision>\S+)\s*\n"
        r"^\s+serial number\s+: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.scripts.get_version()
        r = [
            {
                "type": "CHASSIS",
                "vendor": "Mellanox",
                "part_no": [v["platform"]],
                "serial": v["attributes"]["Serial Number"],
                "revision": v["attributes"]["HW version"],
            }
        ]
        c = self.cli("show interfaces ethernet transceiver")
        for match in self.rx_trans.finditer(c):
            r += [
                {
                    "type": "XCVR",
                    "number": match.group("number"),
                    "vendor": match.group("vendor"),
                    "part_no": match.group("part_no"),
                    "serial": match.group("serial"),
                    "revision": match.group("revision"),
                }
            ]
        return r
