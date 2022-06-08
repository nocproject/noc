# ---------------------------------------------------------------------
# Mellanox.Onyx.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Mellanox.Onyx.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(
        r"^CHASSIS\s+(?P<platform>\S+)\s+(?P<serial>\S+)\s+\S+\s+(?P<hardware>\S+)", re.MULTILINE
    )
    rx_version = re.compile(r"^Product release:\s+(?P<version>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show inventory", cached=True)
        match = self.rx_platform.search(v)
        r = {
            "vendor": "Mellanox",
            "platform": match.group("platform"),
            "attributes": {
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }
        v = self.cli("show version", cached=True)
        match = self.rx_version.search(v)
        r["version"] = match.group("version")
        return r
