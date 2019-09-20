# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Upvel.UP.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Upvel.UP.get_inventory"
    interface = IGetInventory

    def execute_cli(self):
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "UPVEL", "part_no": v["platform"]}]
        try:
            v = self.cli("show ddm")
        except self.CLISyntaxError:
            return r
        for i in parse_table(v, expand_columns=True):
            ifname = i[0]
            vendor = i[1]
            part_no = i[2]
            if not vendor or not part_no:
                continue
            if vendor == "OEM":
                part_no = "NoName | Transceiver | 1G | SFP"
            r += [
                {
                    "type": "XCVR",
                    "vendor": vendor,
                    "part_no": part_no,
                    "number": ifname.split("/")[1],
                    "serial": i[4],
                    "description": ("%s %s" % (i[3], i[5])).strip(),
                }
            ]
        return r
