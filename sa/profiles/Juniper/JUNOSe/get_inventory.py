# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_inventory"
    interface = IGetInventory

    rx_chassis = re.compile(
        r"^Chassis\s+(?P<serial>\d{10})\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<revision>\d+\.\d+)\s*$")
    rx_module = re.compile(
        r"^(?P<slot>\d+)\s+(?P<name>\S+(?: \S+)*)\s+"
        r"(?P<serial>\d{10})?\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<ram>\d+|---)\s+"
        r"(?P<revision>\d+\.\d+)\s*$")
    rx_adapter = re.compile(
        r"^(?P<slot>\d+)/(?P<adapter>\d+)\s+(?P<name>\S+(?: \S+)+?)\s+"
        r"(?P<serial>\d{10})?\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<mac>\d+)\s*$")
    rx_mac = re.compile(
        r"^(?P<slot>\d+/\d+)\s+"
        r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"(?P<revision>\d+\.\d+)\s*$", re.MULTILINE)
    rx_fan = re.compile(
        r"^(?P<slot>\d+)\s+(?P<name>\S+ FAN)\s+"
        r"(?P<serial>\d{10})\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<revision>\d+\.\d+)\s*$")

    def execute(self):
        r = []
        v = self.cli("show hardware")
        for l in v.split("\n"):
            match = self.rx_chassis.search(l)
            if match:
                r += [{
                    "type": "CHASSIS",
                    "vendor": "JUNIPER",
                    "part_no": match.group("part_no"),
                    "serial": match.group("serial"),
                    "revision": match.group("revision")
                }]
            match = self.rx_module.search(l)
            if match:
                r += [{
                    "type": "MODULE",
                    "number": match.group("slot"),
                    "vendor": "JUNIPER",
                    "part_no": match.group("part_no"),
                    "serial": match.group("serial"),
                    "revision": match.group("revision"),
                    "description": match.group("name")
                }]
            match = self.rx_fan.search(l)
            if match:
                r += [{
                    "type": "FAN",
                    "number": match.group("slot"),
                    "vendor": "JUNIPER",
                    "part_no": match.group("part_no"),
                    "serial": match.group("serial"),
                    "revision": match.group("revision"),
                    "description": match.group("name")
                }]
        for l in v.split("\n"):
            match = self.rx_adapter.search(l)
            if match:
                i = 1
                for p in r:
                    if p["type"] == "MODULE" \
                            and p["number"] == match.group("slot"):
                        a = {
                            "type": "ADAPTER",
                            "number": match.group("adapter"),
                            "vendor": "JUNIPER",
                            "part_no": match.group("part_no"),
                            "serial": match.group("serial"),
                            "description": match.group("name")
                        }
                        for m in v.split("\n"):
                            match1 = self.rx_mac.search(m)
                            if match1 \
                                    and match1.group("slot") == \
                                                            match.group("slot") + "/" + match.group("adapter"):
                                a["revision"] = match1.group("revision")
                                break
                        r.insert(i, a)
                        break
                    i += 1
        return r
