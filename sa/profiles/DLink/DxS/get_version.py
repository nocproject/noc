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
        r"Device Type\s+:\s+(?P<platform>\S+).+"
        r"(?:Boot PROM|System [Bb]oot)\s+"
        r"[Vv]ersion\s+:\s+(?:Build\s+)?(?P<bootprom>\S+).+"
        r"[Ff]irmware [Vv]ersion\s+:\s+(?:Build\s+)?(?P<version>\S+).+"
        r"[Hh]ardware [Vv]ersion\s+:\s+(?P<hardware>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_fwt = re.compile(
        r"(?:Firmware Type|System [Ff]irmware [Vv]ersion)\s+:\s+"
        r"(?P<fwt>\S+)\s*\n", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(
        r"(?:[Ss]erial [Nn]umber|Device S/N)\s+:\s+(?P<serial>\S+)\s*\n",
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
