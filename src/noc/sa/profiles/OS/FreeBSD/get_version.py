# ---------------------------------------------------------------------
# OS.FreeBSD.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "OS.FreeBSD.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"(?P<version>\S+)\s+(?P<platform>\S+)")

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("uname -m -r"))
        return {
            "vendor": "FreeBSD",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
