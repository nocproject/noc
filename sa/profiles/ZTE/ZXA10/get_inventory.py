# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXA10.get_inventory
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
    name = "ZTE.ZXA10.get_inventory"
    interface = IGetInventory

    type = {"PRWGS": "PWR", "SCXN": "MAINBOARD", "GUSQ": "LINECARD", "VDWVD": "LINECARD"}
    rx_platform = re.compile(r"^\d+\s+(?P<platform>\S+)MBRack\s+.+\n", re.MULTILINE)
    rx_card = re.compile(
        r"^Real-Type\s+:\s+(?P<type>\S+)\s+Serial-Number\s+:(?P<serial>.*)\n", re.MULTILINE
    )
    rx_detail = re.compile(
        r"^M-CODE\s+:\s+\S+\s+Hardware-VER\s+:\s+(?P<hardware>\S+)\s*\n", re.MULTILINE
    )

    def execute_cli(self):
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "ZTE", "part_no": [v["platform"]]}]
        ports = self.profile.fill_ports(self)
        for p in ports:
            v = self.cli("show card shelfno %s slotno %s" % (p["shelf"], p["slot"]))
            match = self.rx_card.search(v)
            if not match:
                continue
            i = {
                "type": self.type[match.group("type")],
                "number": p["slot"],
                "vendor": "ZTE",
                "part_no": [match.group("type")],
            }
            if match.group("serial").strip():
                i["serial"] = match.group("serial").strip()
            match = self.rx_detail.search(v)
            if match:
                i["revision"] = match.group("hardware")
            r += [i]
        return r
