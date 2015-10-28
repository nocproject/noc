# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_platform = re.compile(r"Card type:\s+(?P<platform>\S+)",
    re.MULTILINE | re.DOTALL)
rx_version = re.compile(r"EXOS version:\s+(?P<version>\S+)",
    re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Extreme.XOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("debug hal show version")
        platform = rx_platform.search(v).group("platform")
        version = rx_version.search(v).group("version")
        return {
            "vendor": "Extreme",
            "platform": platform,
            "version": version
        }
