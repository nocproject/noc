# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"^(?P<platform>.+?)\s+WANFleX\s+(?P<version>\S+)",
                        re.MULTILINE)

    def execute(self):
        cmd = self.cli("system version")
        match = self.rx_ver.search(cmd.strip())
        return {
            "vendor": "InfiNet",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
