# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alstec.MSPU.get_version"
    interface = IGetVersion
    cache = True

    rx_ver1 = re.compile(r"Chip\s\d:\sHW\sVer\s*(?P<hw_ver>\S+)\s*FW\sVer\s(?P<sw_ver>\S+)", re.IGNORECASE)
    rx_ver2 = re.compile(r"^software v\.(?P<version>\S+) ", re.MULTILINE)

    def execute(self):
        try:
            c = self.cli("context dslam version ", cached=True)
            match = self.rx_ver1.search(c)
            return {
                "vendor": "Alstec",
                "platform": "MSPU",
                "version": match.group("sw_ver"),
                "attribute": {
                    "HW version": match.group("hw_ver"),
                }
            }
        except self.CLISyntaxError:
            c = self.cli("version", cached=True)
            match = self.rx_ver2.search(c)
            return {
                "vendor": "Alstec",
                "platform": "MSPU",
                "version": match.group("version")
            }
