# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NextIO.vNet.get_version
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
    name = "NextIO.vNet.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(
        r"Assembly Model Name\s+(?P<platform>.+?)$.*"
        r"Firmware Version\s+(?P<version>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show versions")
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "NextIO",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
