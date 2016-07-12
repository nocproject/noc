# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ALS.7200.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
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
    name = "ALS.7200.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^Machine Type\.+ ALS24300 System - 16 GE, 4\s*\n"
        r"^\s+GE/Stack\s*\n"
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\s*\n"
        r"^Software Version\.+ (?P<version>\S+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        return {
            "vendor": "ALS",
            "platform": "7200",
            "version": match.group("version")
        }
