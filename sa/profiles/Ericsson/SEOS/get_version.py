# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ericsson.SEOS.get_version
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
    name = "Ericsson.SEOS.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"^[^-]*-(?P<version>[^-]+)-.*",
                        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor"   : "Ericsson",
            "platform" : "SEOS",
            "version"  : match.group("version"),
        }
