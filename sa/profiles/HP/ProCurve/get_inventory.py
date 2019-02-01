# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# РЗ.Procurve.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "HP.ProCurve.get_inventory"
    interface = IGetInventory

    rx_chassis = re.compile(
        r"^\s*Chassis:\s+\d\S+\s+(?P<part_no>\S+)\!?\s+Serial Number:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE
    )
    rx_mng = re.compile(
        r"^\s*Management Module:\s+(?P<part_no>\S+)\s+Serial Number:\s+(?P<serial>\S+)\s+",
        re.MULTILINE
    )
    rx_linecard = re.compile(r"^HP (?P<part_no>\S+) \S+", re.MULTILINE)

    def execute_cli(self):
        try:
            v = self.cli("sh mod")
        except self.CLISyntaxError:
            v = self.scripts.get_version()
            return [{
                "type": "CHASSIS",
                "vendor": "HP",
                "part_no": v["platform"]
            }]
        match = self.rx_chassis.search(v)
        r = [{
            "type": "CHASSIS",
            "vendor": "HP",
            "part_no": match.group("part_no"),
            "serial": match.group("serial")
        }]
        match = self.rx_mng.search(v)
        r += [{
            "type": "MODULE",
            "vendor": "HP",
            "part_no": match.group("part_no"),
            "serial": match.group("serial"),

        }]
        t = parse_table(v, allow_wrap=True)
        for i in t:
            match = self.rx_linecard.search(i[1])
            r += [{
                "type": "LINECARD",
                "number": i[0],
                "vendor": "HP",
                "part_no": match.group("part_no"),
                "serial": i[2],
                "revision": i[5],
                "description": i[1]
            }]
        v = self.cli("show system power-supply")
        t = parse_table(v, allow_wrap=True)
        for i in t:
            r += [{
                "type": "PSU",
                "number": i[0],
                "vendor": "HP",
                "part_no": i[1],
                "description": "%s / %s Watt" % (i[3], i[4])
            }]
        return r
