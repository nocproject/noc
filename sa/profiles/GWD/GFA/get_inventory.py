# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GWD.GFA.get_inventory
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
    name = "GWD.GFA.get_inventory"
    interface = IGetInventory
    cache = True

    rx_version = re.compile(r"^ProductOS Version (?P<version>\S+)", re.MULTILINE)
    rx_chassis = re.compile(
        r"^CHASSIS : (?P<part_no>\S+)\s+(?P<revision>\S+)\s+(?P<mfg_date>\d{4}\-\d\d\-\d\d)\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_module = re.compile(
        r"^SLOT\s+(?P<number>\d+) : (?P<part_no>\S+)\s+(?P<revision>\S+)\s+(?P<mfg_date>\d{4}\-\d\d\-\d\d)\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_sfp = re.compile(
        r"^\s+(?P<slot>\d+)/(?P<number>\d+)\s+(?P<vendor>\S+)\s+(?P<part_no>\S+)\s+(?P<serial>\S+)\s+.+\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        p = self.cli("show sfp-online pon")
        u = self.cli("show sfp-online uplink")
        sfp = "%s%s" % (u, p)
        v = self.cli("show version", cached=True)
        match = self.rx_chassis.search(v)
        r = [
            {
                "type": "CHASSIS",
                "vendor": "GWD",
                "serial": match.group("serial"),
                "part_no": [match.group("part_no")],
                "revision": match.group("revision"),
                "mfg_date": match.group("mfg_date"),
            }
        ]
        for match in self.rx_module.finditer(v):
            part_no = match.group("part_no")
            number = match.group("number")
            if "-FAN" in part_no:
                type = "FAN"
            elif "-PWU" in part_no:
                type = "PWR"
            else:
                type = "LINECARD"
            r += [
                {
                    "type": type,
                    "vendor": "GWD",
                    "number": number,
                    "serial": match.group("serial"),
                    "part_no": [match.group("part_no")],
                    "revision": match.group("revision"),
                    "mfg_date": match.group("mfg_date"),
                }
            ]
            if type == "LINECARD":
                for match1 in self.rx_sfp.finditer(sfp):
                    if match1.group("slot") != number:
                        continue
                    r += [
                        {
                            "type": "XCVR",
                            "vendor": match1.group("vendor"),
                            "number": match1.group("number"),
                            "serial": match1.group("serial"),
                            "part_no": [match1.group("part_no")],
                        }
                    ]
        return r
