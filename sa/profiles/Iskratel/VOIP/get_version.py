# ---------------------------------------------------------------------
# Iskratel.VOIP.get_version
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
    name = "Iskratel.VOIP.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(r"^\s*MAIN: (?P<version>\S+)\s*\n", re.MULTILINE)

    def execute(self):
        match = self.rx_ver.search(self.cli("show version"))
        return {"vendor": "Iskratel", "platform": "VOIP", "version": match.group("version")}
