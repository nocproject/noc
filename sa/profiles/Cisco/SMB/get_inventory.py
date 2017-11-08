# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Cisco.SMB.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>[\S ]+)?\s*, "
        r"SN: (?P<serial>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.rx_item.search(self.cli("show inventory"))
        return [{
            "type": "CHASSIS",
            "vendor": "CISCO",
            "part_no": [match.group("pid")],
            "revision": match.group("vid"),
            "serial": match.group("serial"),
            "description": match.group("descr")
        }]
