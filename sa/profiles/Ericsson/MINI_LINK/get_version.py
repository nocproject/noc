# ---------------------------------------------------------------------
# Ericsson.MINI_LINK.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ericsson.MINI_LINK.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Active SBL\s+: CXP: \S+ MINI-LINK (?P<platform>\S+) (?P<version>\S+)", re.MULTILINE
    )

    def execute(self):
        ver = self.cli_clean("show version", cached=True)
        match = self.rx_ver.search(ver)
        return {
            "vendor": "Ericsson",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
