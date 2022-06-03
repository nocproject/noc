# ---------------------------------------------------------------------
# Symbol.AP.get_version
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
    name = "Symbol.AP.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^(?P<platform>AP\S+) version (?P<verions>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_serial = re.compile(r"^System serial number is (?P<serial>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        match1 = self.rx_serial.search(v)
        return {
            "vendor": "Symbol",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Serial Number": match1.group("serial"),
            },
        }
