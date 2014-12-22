# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Aruba.ArubaOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(NOCScript):
    name = "Aruba.ArubaOS.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(
        r"ArubaOS \(MODEL: (?P<platform>.+?)\), Version (?P<version>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Aruba",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
