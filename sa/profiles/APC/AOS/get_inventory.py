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

    @staticmethod
    def part_no_detect(model):
        if "Smart-UPS RT 6000" in model:  # model == "Smart-UPS RT 6000 XL"
            return "SRT6KRMXLI"
        return None

    def execute_cli(self, **kwargs):
        r = []
        ups_map = {"model": "model",
                   "sku": "part_no",
                   "serial number": "serial",
                   "manufacture date": "mfg_date",
                   "battery sku": "battery_part_no"}
        v = self.cli("upsabout")
        d = parse_kv(ups_map, v)
        if d.get("mfg_date"):
            try:
                if len(d["mfg_date"]) == 8:
                    d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%m/%d/%y")
                else:
                    d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%m/%d/%Y")
                d["mfg_date"] = d["mfg_date"].strftime("%Y-%m-%d")
            except ValueError:
                self.logger.warning("Unknown format manufacture date field")
                d["mfg_date"] = None
        if "part_no" not in d and "model" in d:
            # Try normalize
            d["part_no"] = self.part_no_detect(d["model"])
        if d.get("part_no"):
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
            try:
                if len(d["mfg_date"]) == 8:
                    # 08/19/14
                    d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%m/%d/%y")
                else:
                    # 08/19/2014
                    d["mfg_date"] = datetime.datetime.strptime(d["mfg_date"], "%m/%d/%Y")
                d["mfg_date"] = d["mfg_date"].strftime("%Y-%m-%d")
            except ValueError:
                self.logger.warning("Unknown format manufacture date field")
                d["mfg_date"] = None
        if "part_no" in d:
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
