# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
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
        r"^\s*Bootcode Version: (?P<bootprom>\S+)\s*\n"
        r"^\s*Hardware Version: (?P<hardware>\S+)\s*\n"
        r"^\s*Serial Number: (?P<serial>\S+)\s*\n"
        r"^\s*F/W Version: (?P<version>\S+)\s*\n",
        re.MULTILINE)
    rx_chips = re.compile(r"^\s*(?P<platform>\S+)\s+")

    def execute(self):
        slots = self.profile.get_slots_n(self)
        try:
            match = self.rx_ver1.search(self.cli("sys version"))
        except self.CLISyntaxError:
            match = self.rx_ver2.search(self.cli("sys info show"))
        if match:
            platform = self.profile.get_platform(self, slots, match.group("platform"))
        else:
            match = self.rx_ver3.search(self.cli("sys info show"))
            if match:
                match1 = self.rx_chips.search(self.cli("chips info"))
                return {
                    "vendor": "ZyXEL",
                    "platform": match1.group("platform"),
                    "version": match.group("version"),
                    "attributes": {
                        "Boot PROM": match.group("bootprom"),
                        "HW version": match.group("hardware"),
                        "Serial Number": match.group("serial")
                    }
                }
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
