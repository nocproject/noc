# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.iLO2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"version=(?P<version>\S+)")


class Script(BaseScript):
    name = "HP.iLO2.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("show /map1/firmware1/ version")
        match = rx_ver.search(v)
        return {
            "vendor": "HP",
            "platform": "iLO2",
            "version": match.group("version")
        }
