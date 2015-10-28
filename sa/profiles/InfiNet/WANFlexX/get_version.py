# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InfiNet.WANFlexX.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"^(?P<platform>.+?)\s+WANFleX\s+(?P<version>\S+)",
    re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("system version")
        match = rx_ver.search(v.strip())
        return {
            "vendor": "InfiNet",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
