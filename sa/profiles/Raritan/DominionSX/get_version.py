# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raritan.DominionSX.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"Firmware Version : (?P<version>\S+)", re.MULTILINE)


class Script(BaseScript):
    name = "Raritan.DominionSX.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show version")
        match = rx_ver.search(v)
        return {
            "vendor": "Raritan",
            "platform": "SX",
            "version": match.group("version")
        }
