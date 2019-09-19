# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.MXK.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Zhone.MXK.get_inventory"
    cache = True
    interface = IGetInventory

    rx_slot = re.compile(
        r"^\s*(?P<slot_no>a|b|\d+):(?:\*| )(?P<descr>.+?) \(.+\)\s*\n", re.MULTILINE
    )
    rx_card = re.compile(
        r"^CardType\s+: \d+ -- (?P<part_no>\S+)\s*\n"
        r"^CardVersion\s+: (?P<revision>\S+)\s*\n"
        r"^SerialNum\s+: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "ZHONE", "part_no": v["platform"]}]
        for i in ["SHELFME", "BACKPLANE", "FANTRAY"]:
            v = self.cli("eeshow %s 0" % i)
            match = self.rx_card.search(v)
            r += [
                {
                    "type": i,
                    "vendor": "ZHONE",
                    "part_no": match.group("part_no"),
                    "serial": match.group("serial"),
                    "revision": match.group("revision"),
                    "builtin": True,
                }
            ]
        v = self.cli("slots", cached=True)
        for match in self.rx_slot.finditer(v):
            slot_no = match.group("slot_no")
            descr = match.group("descr")
            c = self.cli("eeshow card %s" % slot_no, cached=True)
            match1 = self.rx_card.search(c)
            r += [
                {
                    "type": "LINECARD",
                    "vendor": "ZHONE",
                    "part_no": match1.group("part_no"),
                    "number": slot_no,
                    "serial": match1.group("serial"),
                    "revision": match1.group("revision"),
                    "description": descr,
                }
            ]
        return r
