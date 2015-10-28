# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOSv2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"^(?P<platform>.+?) version (?P<version>.+?)\s+",
    re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Zyxel.ZyNOSv2.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("version")
        match = rx_ver.search(v)
        return {
            "vendor": "Zyxel",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
