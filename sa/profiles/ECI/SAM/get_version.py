# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ECI.SAM.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "ECI.SAM.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"\|\|\s+0\s+\|\|\s+(?P<platform>.+)\s*\n")

    def execute(self):
        self.cli("SHELF")
        c = self.cli("EXISTSH 0 ")
        self.cli("END")
        match = self.rx_platform.search(c)
        platform = match.group("platform")
        return {
            "vendor": "ECI",
            "platform": platform,
            "version": "Unknown"
        }
