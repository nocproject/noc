# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 3Com.SuperStack.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_version = re.compile(r"Operational Version\s+(?P<version>\S+)",
    re.MULTILINE | re.DOTALL)
rx_platform = re.compile(r"\-+3Com\s(?P<platform>[A-Za-z\d\s]+)\-+.*",
    re.MULTILINE | re.DOTALL)


class Script(noc.sa.script.Script):
    name = "3Com.SuperStack.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        p = self.motd
        platform = rx_platform.search(p).group("platform")
        v = self.cli("system display")
        v = v.replace(":", "")
        version = rx_version.search(v).group("version")
        return {
            "vendor": "3Com",
            "platform": platform,
            "version": version
        }
