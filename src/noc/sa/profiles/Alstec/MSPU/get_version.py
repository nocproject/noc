# ---------------------------------------------------------------------
# Alstec.MSPU.get_version
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
    name = "Alstec.MSPU.get_version"
    interface = IGetVersion
    cache = True

    rx_ver1 = re.compile(
        r"Chip\s\d:\sHW\sVer\s*(?P<hw_ver>\S+)\s*FW\sVer\s(?P<sw_ver>\S+)", re.IGNORECASE
    )
    rx_ver2 = re.compile(r"^software v\.(?P<version>\S+) ", re.MULTILINE)
    rx_ver3 = re.compile(r"Build:\s+MKC-IP\s+(?P<platform>\S+)\s+(?P<version>\S+\s+\(\S+\))")

    def execute_cli(self):
        platform = "MSPU"
        try:
            c = self.cli("context dslam version ", cached=True)
            match = self.rx_ver1.search(c)
            return {
                "vendor": "Alstec",
                "platform": platform,
                "version": match.group("sw_ver"),
                "attributes": {"HW version": match.group("hw_ver")},
            }
        except self.CLISyntaxError:
            c = self.cli("version", cached=True)
            match = self.rx_ver2.search(c)
            if not match:
                match = self.rx_ver3.search(c)
                platform = match.group("platform")
            return {"vendor": "Alstec", "platform": platform, "version": match.group("version")}
