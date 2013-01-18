# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Dell.Powerconnect55xx.get_version"
    cache = True
    implements = [IGetVersion]
    rx_55xx_hw = re.compile(
        r"^Type:\s+PowerConnect (?P<platform>\S+)", re.MULTILINE)
    rx_55xx_fw = re.compile(
        r"^\d\s+\d\s+\S+\s+(?P<version>\S+)\s+\S+\s+\S+\s+Active\*",
        re.MULTILINE)
    rx_55xx_ser = re.compile(
        r"^\s+\d\s+(?P<serial>\S+)", re.MULTILINE)

    def execute(self):
        s = self.cli("show system unit 1", cached=True)
        match = self.re_search(self.rx_55xx_hw, s)
        platform = match.group("platform")
        s = self.cli("show bootvar", cached=True)
        match = self.re_search(self.rx_55xx_fw, s)
        version = match.group("version")
        s = self.cli("show system id", cached=True)
        match = self.re_search(self.rx_55xx_ser, s)
        serial = match.group("serial")
        return {
            "vendor": "Dell",
            "platform": platform,
            "version": version,
            "attributes": {
                "Serial Number": serial
            }
        }
