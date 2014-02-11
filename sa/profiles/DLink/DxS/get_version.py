# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "DLink.DxS.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(
        r"Device Type\s+:\s+(?P<platform>\S+).+(?:Boot PROM|System Boot)\s+"
        r"Version\s+:\s+(?:Build\s+)?(?P<bootprom>\S+).+Firmware Version\s+:"
        r"\s+(?:Build\s+)?(?P<version>\S+).+Hardware Version\s+:\s+"
        r"(?P<hardware>\S+)", re.MULTILINE | re.DOTALL)
    rx_fwt = re.compile(
        r"(?:Firmware Type|System Firmware Version)\s+:\s+(?P<fwt>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(
        r"(?:Serial Number|Device S/N)\s+:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        s = self.cli("show switch", cached=True)
        match = self.re_search(self.rx_ver, s)
        r = {
            "vendor": "DLink",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
            }
        }
        ser = self.rx_ser.search(s)
        if (ser and ser.group("serial") != "System" and
            ser.group("serial") != "Power"):
            r["attributes"]["Serial Number"] = ser.group("serial")
        fwt = self.rx_fwt.search(s)
        if fwt:
            r["attributes"]["Firmware Type"] = fwt.group("fwt")
        return r
