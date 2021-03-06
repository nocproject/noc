# ---------------------------------------------------------------------
# ZTE.ZXA10.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# re modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "ZTE.ZXA10.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(
        r"^System Description: (?P<platform>\S+) Version (?P<version>\S+) Software,", re.MULTILINE
    )
    rx_version2 = re.compile(
        r"^ZXA10 (?P<platform>\S+)\s*\n"
        r"^ZTE ZXA10 Software, Version: (?P<version>\S+), Release software",
        re.MULTILINE,
    )

    def execute_cli(self):
        try:
            v = self.cli("show system-group", cached=True)
            match = self.rx_version.search(v)
        except self.CLISyntaxError:
            v = self.cli("show software", cached=True)
            match = self.rx_version2.search(v)
        return {
            "vendor": "ZTE",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
