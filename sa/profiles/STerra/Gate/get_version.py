# ---------------------------------------------------------------------
# STerra.Gate.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "STerra.Gate.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"(?P<ver>\d.\d.\d\S+\s#\d\s\S.+)", re.MULTILINE)

    def execute_snmp(self):
        version = "Unknown"
        s = self.snmp.get("1.3.6.1.2.1.1.1.0")
        match = self.rx_ver.search(s)
        if match:
            version = match.group("ver")
        result = {"vendor": "STerra", "version": version, "platform": "Gate"}
        return result
