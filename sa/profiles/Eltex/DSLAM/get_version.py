# ---------------------------------------------------------------------
# Eltex.DSLAM.get_version
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
    name = "Eltex.DSLAM.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(r"version:\s+(?P<version>\S+)")

    def execute(self):
        try:
            ver = self.cli("system show software info", cached=True)
        except self.CLISyntaxError:
            ver = self.cli("system show software version", cached=True, ignore_errors=True)
        match = self.rx_version.search(ver)
        if match:
            version = match.group("version")
            if "mxa32" in version:
                platform = "MXA32"
            elif "mxa64" in version:
                platform = "MXA64"
            else:
                platform = "DSLAM"
            return {"vendor": "Eltex", "platform": platform, "version": version}
        return {"vendor": "Eltex", "platform": "MXA24", "version": "mxa24"}
