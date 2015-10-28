# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"System Type\s+:\s+(?P<platform>.+?)$",
                        re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(r"System Version\s+:\s+(?P<version>.+?)$",
                        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show system information")
        match_sys = self.re_search(self.rx_sys, v)
        match_ver = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
