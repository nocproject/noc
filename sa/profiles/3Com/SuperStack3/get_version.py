# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 3Com.SuperStack3.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "3Com.SuperStack3.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^3Com\s(?P<platform>[A-Za-z\d\s]+)\n",
        re.MULTILINE)
    rx_version = re.compile(r"^Operational Version:\s+(?P<version>\S+)",
        re.MULTILINE)

    def execute(self):
        v = self.cli("system summary")
        platform = self.rx_platform.search(v).group("platform")
        version = self.rx_version.search(v).group("version")
        return {
            "vendor": "3Com",
            "platform": platform.strip(),
            "version": version
        }
