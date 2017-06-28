# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_inventory
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
    name = "Eltex.ESR.get_inventory"
    interface = IGetInventory
    cache = True

    rx_ver = re.compile(
        r"System type:\s+Eltex\s+(?P<platform>\S+)\s+.+\n"
        r"System name:\s+\S+\s*\n"
        r"Software version:\s+(?P<version>\S+)\s+.+\n"
        r"Hardware version:\s+(?P<hardware>\S+)\s*\n"
        r"System uptime:.+\n"
        r"System MAC address:\s+\S+\s*\n"
        r"System serial number:\s+(?P<serial>\S+)\s*\n")

    def execute(self):
        c = self.scripts.get_system()
        match = self.rx_ver.search(c)
        return [{
            "type": "CHASSIS",
            "vendor": "ELTEX",
            "part_no": match.group("platform"),
            "serial": match.group("serial"),
            "revision": match.group("hardware")
        }]
