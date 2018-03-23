# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# APC.AOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import datetime
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_kv


class Script(BaseScript):
    name = "APC.AOS.get_inventory"
    cache = True
    interface = IGetInventory

    def execute(self, **kwargs):
        r = []
        ups_map = {"model": "model",
                   "sku": "part_no",
                   "serial number": "serial",
                   "manufacture date": "mfg_date",
                   "battery sku": "battery_part_no"}
        v = self.cli("upsabout")
        d = parse_kv(ups_map, v)
        if d.get("mfg_date"):
            d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%m/%d/%Y")
            d["mfg_date"] = d["mfg_date"].strftime("%Y-%m-%d")
        r += [{
                "type": "CHASSIS",
                "number": 1,
                "vendor": "APC",
                "serial": d["serial"],
                "mfg_date": d.get("mfg_date", "00-00-00"),
                "description": d["model"],
                "part_no": d["part_no"],
            }]
        mgmt_card_map = {"model number": "part_no",
                         "serial number": "serial",
                         "hardware revision": "revision",
                         "manufacture date": "mfg_date",
                         "battery sku": "battery_part_no"}
        v = self.cli("about", cached=True)
        d = parse_kv(mgmt_card_map, v)
        if d.get("mfg_date"):
            d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%m/%d/%Y")
            d["mfg_date"] = d["mfg_date"].strftime("%Y-%m-%d")
        r += [{
                "type": "MGMT",
                "number": 1,
                "vendor": "APC",
                "serial": d["serial"],
                "description": "Management card",
                "mfg_date": d.get("mfg_date", "00-00-00"),
                "revision": d["revision"],
                "part_no": d["part_no"],
            }]

        return r
