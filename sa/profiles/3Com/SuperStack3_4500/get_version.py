# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(
        r"^SuperStack 3 Switch (?P<platform>\S+).+Software Version (?P<version>.+)$",
        re.MULTILINE,
    )
    rx_version2 = re.compile(
        r"^Switch (?P<platform>\S+).+Software Version 3Com OS (?P<version>.+)$",
        re.MULTILINE,
    )
    rx_dev = re.compile(
        r"0\s+0\s+\d+\s+(?P<hardware>\S+)\s+\S+\s+\S+\s+(?P<bootprom>\S+)", re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("display version", cached=True)
        match = self.rx_version.search(v)
        if not match:
            match = self.rx_version2.search(v)
        v = self.cli("display device", cached=True)
        match1 = self.rx_dev.search(v)
        return {
            "vendor": "3Com",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match1.group("bootprom"),
                "HW version": match1.group("hardware"),
            },
        }
