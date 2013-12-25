# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_inventory"
    implements = [IGetInventory]

    rx_trans = re.compile(r"Port\s+:\s+(?P<number>\d+)\s+\S+."
                r"Vendor\s+:\s+(?P<vendor>\S+)\s*."
                r"Part Number\s+:\s+(?P<part_no>\S+)\s*."
                r"Serial Number\s+:\s+(?P<serial>\S+)\s*."
                r"Revision\s+:\s+(?P<rev>\S+)?\s*."
                r"Date Code\s+:\s+\S+."
                r"Transceiver\s+:\s+(?P<type>\S+)",
                re.MULTILINE | re.DOTALL)

    trans_map = {
        "1000BASE-L": "Unknown | Transceiver | 1000BASE-LX"
    }

    def execute(self):
        objects = []
        v = self.scripts.get_version()
        part_no = v["platform"]
        vendor = v["vendor"]
        objects += [{
            "type": "CHASSIS",
            "number": 1,
            "vendor": vendor,
            "description": part_no,
            "part_no": [part_no],
            "builtin": False
        }]
        objects += self.get_transceivers()
        return objects

    def get_transceivers(self):
        if self.match_version(platform__contains="2024"):
            XN = lambda x: str(int(x) + 24)
        elif self.match_version(platform__contains="2108"):
            XN = lambda x: str(int(x) + 8)
        else:
            XN = lambda x: x
        objects = []
        if self.match_version(version__startswith="3.90"):
            inv = self.cli("show interface transceiver *")
            for match in self.rx_trans.finditer(inv):
                objects += [{
                    "type": "XCVR",
                    "number": XN(match.group("number")),
                    "vendor": match.group("vendor"),
                    "serial": match.group("serial"),
                    "description": match.group("type"),
                    "part_no": [match.group("part_no")],
                    "revision": match.group("rev"),
                    "builtin": False
                }]
        else:
            with self.zynos_mode():
                inv = self.cli("sys sw sfp disp2")
                for idx, vendor, pn, sn in parse_table(inv):
                    if not vendor and not pn and not sn:
                        continue
                    if vendor == "OEM":
                        vendor = "NoName"
                        if pn in self.trans_map:
                            pn = self.trans_map[pn]
                        else:
                            raise self.UnexpectedResultError(
                                "Unknown transceiver type: %s" % pn)
                    objects += [{
                        "type": "XCVR",
                        "number": XN(idx),
                        "vendor": vendor,
                        "serial": sn,
                        "description": pn,
                        "part_no": [pn],
                        "builtin": False
                    }]
        return objects
