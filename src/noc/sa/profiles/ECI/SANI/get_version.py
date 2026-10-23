# ----------------------------------------------------------------------
# ECI.SANI.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "ECI.SANI.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^\s*NI CARD TYPE\s+: (?P<platform>.+)\n^\s*NI SW VERSION NAME\s+: (?P<version>.+)\n",
        re.MULTILINE,
    )

    def execute(self):
        match = self.rx_ver.search(self.cli("ver"))
        return {
            "vendor": "ECI",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
