# ---------------------------------------------------------------------
# Siklu.EH.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Siklu.EH.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"^system description\s+: (?P<platform>.+?)$", re.MULTILINE)
    rx_ver = re.compile(r"^\d+\s+(?P<version>\S+)\s+(\S+\s+\S+\s+)?yes\s+\S+\s+\S+", re.MULTILINE)

    def execute(self):
        v = self.cli("show sw")
        match_ver = self.re_search(self.rx_ver, v)

        v = self.cli("show system description")
        match_sys = self.re_search(self.rx_sys, v)
        return {
            "vendor": "Siklu",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version"),
        }
