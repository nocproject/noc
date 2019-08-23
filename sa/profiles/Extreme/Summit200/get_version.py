# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.Summit200.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Extreme.Summit200.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(
        r"^System Serial Number\s*:\s*(?P<platform>\S+)\s+(?P<serial>.+?)\s\s+.+\n"
        r"^Image\s*:\s*Extremeware\s+Version (?P<version>\S+)\s.+\n"
        r"^\s*\n"
        r"^BootROM\s*:\s*(?P<bootprom>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show version detail")
        match = self.rx_version.search(v)
        return {
            "vendor": "Extreme",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "Serial Number": match.group("serial"),
            },
        }
