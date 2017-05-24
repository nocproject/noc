# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP3.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
 
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Huawei.VRP3.get_inventory"
    interface = IGetInventory

    rx_slot = re.compile(
        r"^\s*FrameId:0 slotId:\s*(?P<number>\d+)\s*\n"
        r"^\s*\S+ Board:\s*\n"
        r"^\s*Pcb\s+Version:\s*(?P<part_no>\S+)\s+VER.(?P<revision>\S+)\s*\n",
        re.MULTILINE)

    def execute(self):
        r = []
        v = self.scripts.get_version()
        platform = v["platform"]
        r += [{
            "type": "CHASSIS",
            "vendor": "HUAWEI",
            "part_no": platform,
        }]
        v = self.cli("show version 0")
        for match in self.rx_slot.finditer(v):
            r += [{
                "type": "LINECARD",
                "number": match.group("number"),
                "vendor": "HUAWEI",
                "part_no": match.group("part_no"),
                "revision": match.group("revision")
            }]
        return r
