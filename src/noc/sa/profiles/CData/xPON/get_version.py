# ---------------------------------------------------------------------
# CData.xPON.get_version
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
    name = "CData.xPON.get_version"
    cache = True
    interface = IGetVersion

    rx_platf = re.compile(
        r"^\s+Device model\s+: (?P<platform>\S+)\n"
        r"^\s+Device MAC address\s+: (?P<mac>\S+)\n"
        r"^\s+Device serial-number\s+: (?P<serial>\S+)\n",
        re.MULTILINE,
    )
    rx_ver = re.compile(
        r"^\s+Hardware version\s+:\s+V?(?P<hardware>\S+)\n"
        r"^\s+Firmware version\s+:\s+V?(?P<version>\S+)\s+",
        re.MULTILINE,
    )

    def execute_cli(self):
        p = self.cli("show device", cached=True)
        match = self.rx_platf.search(p)
        v = self.cli("show version", cached=True)
        match1 = self.rx_ver.search(v)
        if match:
            return {
                "vendor": "CData",
                "platform": match.group("platform"),
                "version": match1.group("version"),
                "attributes": {
                    "HW version": match1.group("hardware"),
                    "Serial Number": match.group("serial"),
                },
            }
        raise self.NotSupportedError()
