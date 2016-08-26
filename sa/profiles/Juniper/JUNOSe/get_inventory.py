# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_inventory"
    interface = IGetInventory

    rx_chassis = re.compile(
        r"^Chassis\s+(?P<serial>\d{10})\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<revision>\d+\.\d+)\s*$")
    rx_module = re.compile(
        r"^(?P<slot>\d+)\s+(?P<name>\S+(?: \S+)+?)\s+"
        r"(?P<serial>\d{10})?\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<ram>\d+|---)\s+"
        r"(?P<revision>\d+\.\d+)\s*$")
    rx_adapter = re.compile(
        r"^(?P<slot>\d+/\d+)\s+(?P<name>\S+(?: \S+)+?)\s+"
        r"(?P<serial>\d{10})?\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<mac>\d+)\s*$")
    rx_fan = re.compile(
        r"^(?P<slot>\d+)\s+(?P<name>\S+ FAN)\s+"
        r"(?P<serial>\d{10})\s+(?P<part_no>\d{10})\s+"
        r"(?P<assembly_rev>\S{3})\s+(?P<revision>\d+\.\d+)\s*$")

    def execute(self):
        r = []
        for l in self.cli("show hardware").split("\n"):
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
            """
            match = self.rx_adapter.search(l)
            if match:
                r += [{
                    "type": "SUB",
                    "number": match.group("slot"),
                    "vendor": "JUNIPER",
                    "part_no": match.group("part_no"),
                    "serial": match.group("serial"),
                    "revision": match.group("revision"),
                    "description": match.group("name")
                }]
            """
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
        return r
