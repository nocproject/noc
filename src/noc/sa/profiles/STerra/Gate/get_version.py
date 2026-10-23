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
    rx_ver = re.compile(r"(?P<version>\d.\d.\d\S+\s#\d\s\S.+)", re.MULTILINE)
    rx_ver42 = re.compile(
        r"S-Terra\s(?P<platform>\S+\s\d.\d.\d+),\s.+, Version (?P<version>\S+), ", re.MULTILINE
    )

    def execute_snmp(self):
        version = "Unknown"
        platform = "Gate"
        s = self.snmp.get("1.3.6.1.4.1.9.9.25.1.1.1.2.7")
        match = self.rx_ver.search(s)
        match42 = self.rx_ver42.search(s)
        if match:
            version = match.group("version")
        if match42:
            version = match42.group("version")
            platform = match42.group("platform")
        return {"vendor": "STerra", "version": version, "platform": platform}
