# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Sun.iLOM3.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r"SP firmware (?P<version>\S+)")


class Script(BaseScript):
    name = "Sun.iLOM3.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("version")
        match = rx_ver.search(v)
        return {
            "vendor": "Sun",
            "platform": "iLOM3",
            "version": match.group("version")
        }
