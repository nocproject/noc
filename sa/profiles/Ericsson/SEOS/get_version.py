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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Ericsson.SEOS.get_version"
    cache = True
    implements = [IGetVersion]
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
