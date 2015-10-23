# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Vyatta.Vyatta.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"^Version:\s+(?P<version>(?:VyOS )?\S+)",
                        re.MULTILINE)

    def execute(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v)
        version = match.group("version")
        if "VyOS" in version:
            vendor, version = match.group("version").split(" ")
            platform = "VyOS"
        else:
            vendor = "Vyatta"
            platform = "VC"
        return {
            "vendor": vendor,
            "platform": platform,
            "version": version
        }
