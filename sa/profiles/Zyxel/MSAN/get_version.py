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
        r"^\s*Model: (?P<platform>\S+)\s*\n"
        r"^\s*ZyNOS version: (?P<version>\S+) \| \S+\s*\n"
        r".+?\n"
        r"^\s*Bootbase version: (?P<bootprom>\S+) \| \S+\s*\n"
        r".+?\n"
        r"^\s*Serial number: (?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        slots = self.profile.get_slots_n(self)
        try:
            match = self.rx_ver1.search(self.cli("sys version"))
        except self.CLISyntaxError:
            match = self.rx_ver2.search(self.cli("sys info show"))
        platform = self.profile.get_platform(self, slots, match.group("platform"))
        return {
            "vendor": "ZyXEL",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom")
            }
        }
