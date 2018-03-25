# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "SKS.SKS.get_inventory"
    interface = IGetInventory
    cache = True

    def execute(self):
        v = self.cli("show version")
        if "Unit" in v:
            stack = {}
            r = []
            t = parse_table(v)
            for i in t:
                stack[i[0]] = {
                    "type": "CHASSIS",
                    "vendor": "SKS",
                    "revision": i[3]
                }
            v = self.cli("show system", cached=True)
            t = parse_table(v, footer="Unit\s+Temperature")
            for i in t:
                platform = i[1]
                if platform == "SKS 10G":
                    platform = "SKS-16E1-IP-1U"
                elif platform.startswith("SKS"):
                    platform = "SW-24"
                if not i[0]:
                    break
                stack[i[0]]["part_no"] = platform
            v = self.cli("show system id", cached=True)
            t = parse_table(v)
            for i in t:
                stack[i[0]]["serial"] = i[1]
            for i in stack:
                r += [stack[i]]
            return r
        else:
            v = self.scripts.get_version()
            r = {
                "type": "CHASSIS",
                "vendor": "SKS",
                "part_no": v["platform"],
                "revision": v["attributes"]["HW version"]
            }
            if "Serial Number" in v["attributes"]:
                r["serial"] = v["attributes"]["Serial Number"]

        return [r]
