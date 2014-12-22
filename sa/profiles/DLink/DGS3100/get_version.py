# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re


class Script(noc.sa.script.Script):
    name = "DLink.DGS3100.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(
        r"Device Type\s+:\s+(?P<platform>\S+).+Boot PROM Version\s+:\s+"
        r"(?:Build\s+)?(?P<bootprom>\S+).+Firmware Version\s+:\s+"
        r"(?:Build\s+)?(?P<version>\S+).+Hardware Version\s+:\s+"
        r"(?P<hardware>\S+)", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(
        r"Serial Number\s+:\s+(?P<serial>.+)\nSystem Name",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        s = self.cli("show switch", cached=True)
        match = self.re_search(self.rx_ver, s)
        r = {"vendor": "DLink",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware")
            }
        }
        ser = self.rx_ser.search(s)
        r["attributes"].update({"Serial Number": ser.group("serial")})
        return r
