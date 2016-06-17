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

    rx_ver = re.compile(
        r"^\s*product model\s*:\s+(?P<platform>\S+)\s*\n"
        r"^\s*system up time\s*:\s+(?P<uptime>\S+)\s*\n"
        r"^\s*f/w version\s*:\s+(?P<version>\S+) \| \S+\s*\n"
        r"^\s*bootbase version\s*:\s+(?P<bootprom>\S+) \| \S+\s*\n",
        re.MULTILINE)

    def execute(self):
        slots = self.profile.get_slots_n(self)
        match = self.rx_ver.search(self.cli("sys version"))
        platform = self.profile.get_platform(self, slots, match.group("platform"))
        return {
            "vendor": "ZyXEL",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom")
            }
        }
