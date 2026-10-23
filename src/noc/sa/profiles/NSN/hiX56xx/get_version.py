# ---------------------------------------------------------------------
# NSN.hiX56xx.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "NSN.hiX56xx.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"System version\s+:\s+(?P<platform>\S+)/(?P<version>\S+)")

    def execute(self):
        v = self.cli("show system-version", cached=True)
        match = self.rx_ver.search(v)
        return {
            "vendor": "NSN",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
