# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Iskratel.MBAN.get_inventory"
    interface = IGetInventory

    rx_inv = re.compile(
        r"^\s*(?P<number>\d+)\s+\S+\s+\S+\s+(?P<part_no>U\S+)\s+"
        r"(?P<serial>[NZ]\S+)\s+", re.MULTILINE)

    def execute(self):
        match = self.rx_inv.search(self.cli("show board"))
        r = {
            "type": "LINECARD",
            "number": match.group("number"),
            "vendor": "ISKRATEL",
            "part_no": match.group("part_no")
        }
        if match.group("serial") != "N/A":
            r["serial"] = match.group("serial")
        return [r]
