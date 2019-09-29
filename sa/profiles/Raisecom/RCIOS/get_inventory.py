# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Raisecom.RCIOS.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_inventory"
    interface = IGetInventory
    cache = True

    kv_map = {
        "version": "version",
        "device": "platform",
        "serial number": "serial",
        "bootrom version": "bootprom",
        "ios version": "hw_version",
        "mainboard": "prod_version",
    }

    def execute(self):
        v = self.cli("show version", cached=True)
        r = parse_kv(self.kv_map, v, sep=":")
        if "prod_version" in r:
            r["prod_version"] = r["prod_version"].split(":")[-1].strip(" .")
        return [
            {
                "type": "CHASSIS",
                "number": "0",
                "vendor": "Raisecom",
                "part_no": r["platform"],
                "revision": r["prod_version"],
                "serial": r["serial"],
                "description": "",
            }
        ]
