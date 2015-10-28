# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Nortel.BayStack425.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Nortel.BayStack425.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^sysDescr:\s+(?P<platform>.+?)  ",
                             re.MULTILINE | re.DOTALL)
    rx_version = re.compile(r" SW:(?P<version>\S+)$", re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show sys-info")
        platform = self.re_search(self.rx_platform, v).group("platform")
        version = self.re_search(self.rx_version, v).group("version")
        return {
            "vendor": "Nortel",
            "platform": platform,
            "version": version
        }
