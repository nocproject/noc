# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
 
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Siklu.EH.get_inventory"
    interface = IGetInventory

    rx_component = re.compile(
        r"^\s*inventory (?P<number>\d+) desc\s+: (?P<description>.*)\n"
        r"^\s*inventory \d+ cont-in\s+: .*\n"
        r"^\s*inventory \d+ class\s+: (?P<type>\S+)\n"
        r"^\s*inventory \d+ rel-pos\s+: .*\n"
        r"^\s*inventory \d+ name\s+: .*\n"
        r"^\s*inventory \d+ hw-rev\s+: (?P<revision>\S+)?\n"
        r"^\s*inventory \d+ fw-rev\s+: .*\n"
        r"^\s*inventory \d+ sw-rev\s+: .*\n"
        r"^\s*inventory \d+ serial\s+: (?P<serial>\S+)?\n"
        r"^\s*inventory \d+ mfg-name\s+: (?P<vendor>\S+)?\n"
        r"^\s*inventory \d+ model-name\s+: (?P<part_no>\S+)?\n"
        r"^\s*inventory \d+ fru\s+: (?P<fru>\S+)\n",
        re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("show inventory")
        for match in self.rx_component.finditer(v):
            if match.group("vendor"):
                vendor = match.group("vendor").upper()
            else:
                vendor = "NONAME"
            p = {
                "type": match.group("type").upper(),
                "number": int(match.group("number") or 0),
                "vendor": vendor,
                "part_no": match.group("part_no"),
                "revision": match.group("revision"),
                "description": match.group("description")
            }
            if match.group("fru") == "false":
                p["builtin"] = True
            if match.group("serial"):
                p["serial"] = match.group("serial")
            r += [p]
        return r
