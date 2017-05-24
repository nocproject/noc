# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.get_inventory
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
    name = "Zyxel.MSAN.get_inventory"
    interface = IGetInventory

    rx_slot = re.compile(
        r"^\s*slot(?P<number>\d+):\s*\n"
        r"^\s*name\s*:\s+(?P<part_no>\S+)\s*\n"
        r"^.+?\n"
        r"^\s*hardware version\s*:\s+(?P<revision>\S+)\s*\n"
        r"^\s*hardware serial number\s*:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_hw = re.compile(
        r"^\s*Model\s*:\s+(?:\S+ \/ )?(?P<part_no>\S+)\s*\n"
        r"^.+?\n"
        r"^\s*Hardware version\s*:\s+(?P<revision>\S+)\s*\n"
        r"^\s*Serial number\s*:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_hw2 = re.compile(
        r"^\s*Hardware Version: (?P<revision>\S+)\s*\n"
        r"^\s*Serial Number: (?P<serial>\S+)\s*\n",
        re.MULTILINE)
    rx_chips = re.compile(r"^\s*(?P<platform>\S+)\s+")

    def execute(self):
        r = []
        slots = self.profile.get_slots_n(self)
        if slots > 1:
            for i in range(1, slots):
                match = self.rx_slot.search(self.cli("lcman show %s" % i))
                if match:
                    part_no = match.group("part_no")
                    r += [{
                        "type": "LINECARD",
                        "number": match.group("number"),
                        "vendor": "ZYXEL",
                        "part_no": match.group("part_no"),
                        "serial": match.group("serial"),
                        "revision": match.group("revision")
                    }]
                    c = self.profile.get_platform(self, slots, part_no)
                    if c:
                        r.insert(0, {
                            "type": "CHASSIS",
                            "vendor": "ZYXEL",
                            "part_no": c,
                        })
        else:
            match = self.rx_hw.search(self.cli("sys info show"))
            if match:
                c = self.profile.get_platform(self, slots, match.group("part_no"))
            else:
                match1 = self.rx_chips.search(self.cli("chips info"))
                c = match1.group("platform")
                match = self.rx_hw2.search(self.cli("sys info show"))
            return [{
                "type": "CHASSIS",
                "vendor": "ZYXEL",
                "part_no": c,
                "serial": match.group("serial"),
                "revision": match.group("revision")
            }]
        return r
