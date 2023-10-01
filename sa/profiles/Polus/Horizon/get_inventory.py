# ---------------------------------------------------------------------
# Polus.Horizon.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from datetime import datetime

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Polus.Horizon.get_inventory"
    interface = IGetInventory

    rx_devices = re.compile(r"(?P<slot>\d+)\s*\|(?P<name>\S+)\s*")
    rx_table = re.compile(r"(?P<pname>\S+)\s*\|(?P<punits>\S*)\s*\|(?P<pvalue>.+)\s*")

    def parse_table(self, v):
        r = {}
        for match in self.rx_table.finditer(v):
            r[match.group("pname")] = match.group("pvalue").strip()
        return r

    def execute_http(self, **kwargs):
        ...

    def execute_cli(self):
        r = [{"type": "CHASSIS", "number": "1", "vendor": "Polus", "part_no": "K8"}]
        v = self.cli("show devices")
        for match in self.rx_devices.finditer(v):
            slot = match.group("slot")
            v = self.cli(f"show params {slot}")
            o = self.parse_table(v)
            r += [{
                "type": "LINECARD",
                "vendor": "Polus",
                "number": slot,
                "part_no": match.group("name"),
                "serial": o["SrNumber"],
                "revision": o["HwNumber"],
            }]
        return r
