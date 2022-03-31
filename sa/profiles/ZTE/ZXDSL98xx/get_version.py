# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# re modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^(?P<platform>ZXDSL98\S+).+\n"
        r"^\s*\n"
        r"^The active version file name is: .+\n"
        r"^Main version name\s+: (?P<version>\S+)",
        re.MULTILINE,
    )
    rx_ver2 = re.compile(
        r"^SCC[FV]\s+MVER\s+V(?P<version>\S+)\s+\d+\s+VALID\s+\d+\s+active\s+(?P<platform>\S+)[Vv]\S+",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        if match:
            return {
                "vendor": "ZTE",
                "platform": match.group("platform"),
                "version": match.group("version"),
            }
        match = self.rx_ver2.search(v)
        if match:
            return {
                "vendor": "ZTE",
                "platform": "ZXDSL %s" % match.group("platform").upper(),
                "version": match.group("version"),
            }
        raise self.NotSupportedError()
