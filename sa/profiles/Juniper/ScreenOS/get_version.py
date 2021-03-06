# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx = re.compile(
    r"Product Name:\s+(?P<platform>\S+)$.+Software Version:\s+(?P<version>.+?)\s*\,",
    re.MULTILINE | re.DOTALL,
)


class Script(BaseScript):
    name = "Juniper.ScreenOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("get system")
        match = rx.search(v)
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
