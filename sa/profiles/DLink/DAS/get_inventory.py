# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DAS.get_inventory
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
    name = "DLink.DAS.get_inventory"
    interface = IGetInventory

    rx_serial = re.compile(r"Serial\s+Number\s*:\s*(?P<serial>\<\S+\>|\S+)")

    def execute_cli(self, **kwargs):
        v = self.cli("get system manuf info", cached=True)
        serial = self.rx_serial.search(v)
        v = self.scripts.get_version()
        return [
            {
                "type": "CHASSIS",
                "number": 0,
                "vendor": "DLink",
                "part_no": v["platform"],
                "serial": serial.group("serial").strip("<> "),
                "description": "",
            }
        ]
