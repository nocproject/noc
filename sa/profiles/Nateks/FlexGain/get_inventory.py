# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.FlexGain.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
import re


class Script(BaseScript):
    name = "Nateks.FlexGain.get_inventory"
    interface = IGetInventory

    rx_chassis = re.compile(
        r"^\s+Card Model\s*:.*\n"
        r"^\s+System Description\s*:(?P<description>.+)\n"
        r"^\s+Hardware Version\s*:.*\n"
        r"^\s+Firmware Version\s*:.*\n"
        r"^\s+Software Version\s*:.*\n"
        r"^\s+Model Information\s*:(?P<part_no1>.+)\n"
        r"^\s+Part Number\s*:(?P<part_no>.+)\n"
        r"^\s+HW Revision\s*:(?P<revision>.+)\n"
        r"^\s+S/N\s*:(?P<serial>.+)\n"
        r"^\s+Manufacture\s*:.*\n",  # Need more examples
        re.MULTILINE)
    rx_slot = re.compile(
        r"^\s+Slot\s+(?P<number>\d+)\s*\n"
        r"^\s+Card Type\s*:(?P<description>.+)\n"
        r"^\s+CPLD Version\s*:.*\n"
        r"^\s+Hardware Version\s*:.*\n"
        r"^\s+Firmware Version\s*:.*\n"
        r"^\s+Model Information\s*:(?P<part_no1>.+)\n"
        r"^\s+Part Number\s*:(?P<part_no>.+)\n"
        r"^\s+HW Revision\s*:(?P<revision>.+)\n"
        r"^\s+Manufacture\s*:.*\n"  # Need more examples
        r"^\s+S/N\s*:(?P<serial>.+)\n",
        re.MULTILINE)


    def execute(self):
        r = []
        v = self.cli("show system inventory")
        match = self.rx_chassis.search(v)
        r += [{
            "type": "CHASSIS",
            "vendor": "Nateks",
            "part_no": [match.group("part_no").strip(), match.group("part_no1").strip()],
            "revision": match.group("revision").strip(),
            "serial": match.group("serial").strip(),
            "description": match.group("description").strip()
        }]
        for match in self.rx_slot.finditer(v):
            r += [{
                "number": match.group("number"),
                "type": "LINECARD",
                "vendor": "Nateks",
                "part_no": [match.group("part_no").strip(), match.group("part_no1").strip()],
                "revision": match.group("revision").strip(),
                "serial": match.group("serial").strip(),
                "description": match.group("description").strip()
            }]

        return r
