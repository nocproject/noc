# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"(?P<platform>\S+) L2/L3 Ethernet Blade Switch.+Software Version (?P<version>\S+)", re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "HP.GbE2.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("/info/sys/general")
        self.cli("/")
        match = rx_ver.search(v)
        return {
            "vendor": "HP",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
