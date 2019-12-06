# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_inventory
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
    name = "Siklu.EH.get_inventory"
    interface = IGetInventory

    rx_component = re.compile(
        r"\s*inventory (?P<number>\d+) desc\s+: (?P<description>.*)"
        r"\s*inventory \d+ cont-in\s+: .*"
        r"\s*inventory \d+ class\s+: (?P<type>\S+)"
        r"\s*inventory \d+ rel-pos\s+: .*"
        r"\s*inventory \d+ name\s+: (?P<name>.*)"
        r"\s*inventory \d+ hw-rev\s+: (?P<revision>(\S+|\S+\s\S+))?\s*"
        r"\s*inventory \d+ fw-rev\s+: (?P<fwrevision>.*)"
        r"\s*inventory \d+ sw-rev\s+: (?P<swrevision>.*)"
        r"\s*inventory \d+ serial\s+: (?P<serial>\S+)?\s*"
        r"\s*inventory \d+ mfg-name\s+: (?P<vendor>\S+)?\s*"
        r"\s*inventory \d+ model-name\s+: (?P<part_no>\S+)?\s*"
        r"\s*inventory \d+ fru\s+: (?P<fru>.*)",
        re.MULTILINE,
    )

    def execute(self):
        r = []
        v = self.cli("show inventory")
        for match in self.rx_component.finditer(v):
            if match.group("vendor"):
                vendor = match.group("vendor").upper()
            else:
                vendor = "NONAME"
            part_no = match.group("part_no")
            if not part_no or part_no == "default":
                continue
            revision = match.group("revision")
            if part_no == "EH-1200TL-ODU-1ft" and revision == "F0":
                part_no = "EH-1200TL-ODU-1ft-F0"
            p = {
                "type": match.group("type").upper(),
                "number": int(match.group("number") or 0),
                "vendor": vendor,
                "part_no": part_no,
                "revision": revision,
                "description": match.group("description"),
            }
            if match.group("fru") == "false":
                p["builtin"] = True
            if match.group("serial"):
                p["serial"] = match.group("serial")
            r += [p]
        return r
