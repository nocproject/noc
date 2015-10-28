# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.CatOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_platform = re.compile(r"^Hardware\s+Version:\s+(?:\d|\.)+\s+Model:\s+(?P<platform>\S+)\s+Serial\s+#:\s+\S+$", re.MULTILINE | re.DOTALL)
rx_version = re.compile(r"^\S+\s+Software,\s+Version\s+\S+:\s+(?P<version>\S+)", re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Cisco.CatOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show version")
        platform = rx_platform.search(v).group("platform")
        version = rx_version.search(v).group("version")
        return {
            "vendor": "Cisco",
            "platform": platform,
            "version": version
        }
