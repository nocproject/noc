# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Zyxel.MSAN.get_version"
    interface = IGetVersion
    cache = True

    rx_ver1 = re.compile(
        r"^\s*product model\s*:\s+(?P<platform>\S+)\s*\n"
        r"^\s*system up time\s*:\s+(?P<uptime>\S+)\s*\n"
        r"^\s*f/w version\s*:\s+(?P<version>\S+) \| \S+\s*\n"
        r"^\s*bootbase version\s*:\s+(?P<bootprom>\S+) \| \S+\s*\n",
        re.MULTILINE)
    rx_ver2 = re.compile(
        r"^\s*Model: (?:\S+ \/ )?(?P<platform>\S+)\s*\n"
        r"^\s*ZyNOS version: (?P<version>\S+) \| \S+\s*\n"
        r".+?\n"
        r"^\s*Bootbase version: (?P<bootprom>\S+) \| \S+\s*\n"
        r".+?\n"
        r"(^\s*Hardware version: (?P<hardware>\S+)\s*\n)?"
        r"^\s*Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_ver3 = re.compile(
        r"^\s*ZyNOS version\s*: (?P<version>\S+) \| \S+\s*\n"
        r".+?\n"
        r".+?\n"
        r"^\s*bootbase version\s*: (?P<bootprom>\S+)"
        r"\((?P<platform>MSC\S+)\) \| \S+\s*\n",
        re.MULTILINE)
    rx_ver4 = re.compile(
        r"^\s*Bootcode Version: (?P<bootprom>.+)\s*\n"
        r"^\s*Hardware Version: (?P<hardware>.+)\s*\n"
        r"^\s*Serial Number: (?P<serial>.+)\s*\n"
        r"^\s*F/W Version: (?P<version>\S+)\s*\n",
        re.MULTILINE)
    rx_chips = re.compile(r"^\s*(?P<platform>\S+?)(/\S+)?\s+")

    def execute(self):
        slots = self.profile.get_slots_n(self)
        try:
            c = self.cli("sys version")
            match = self.rx_ver1.search(c)
        except self.CLISyntaxError:
            c = self.cli("sys info show", cached=True)
            match = self.rx_ver2.search(c)
            if not match:
                match = self.rx_ver3.search(c)
        if match:
            platform = self.profile.get_platform(
                self, slots, match.group("platform")
            )
        else:
            match = self.rx_ver4.search(self.cli("sys info show", cached=True))
            if match:
                match1 = self.rx_chips.search(self.cli("chips info"))
                r = {
                    "vendor": "ZyXEL",
                    "platform": match1.group("platform"),
                    "version": match.group("version")
                }
                if match.group("bootprom") != "not defined":
                    if "attributes" not in r:
                        r["attributes"] = {}
                    r["attributes"]["Boot PROM"] = match.group("bootprom")
                if match.group("hardware") != "not defined":
                    if "attributes" not in r:
                        r["attributes"] = {}
                    r["attributes"]["HW version"] = match.group("hardware")
                if match.group("serial") != "not defined":
                    if "attributes" not in r:
                        r["attributes"] = {}
                    r["attributes"]["Serial Number"] = match.group("serial")
                return r
            else:
                raise self.NotSupportedError()
        r = {
            "vendor": "ZyXEL",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom")
            }
        }
        if ("hardware" in match.groupdict()) and (match.group("hardware")):
            r["attributes"]["HW version"] = match.group("hardware")
        if ("serial" in match.groupdict()) and (match.group("serial")):
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
