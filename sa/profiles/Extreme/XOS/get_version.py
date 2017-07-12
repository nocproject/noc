# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Extreme.XOS.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^Card type:\s+(?P<platform>\S+)", re.MULTILINE)
    rx_version = re.compile(
        r"^(?:EXOS )?[Vv]ersion:\s+(?P<version>\S+)", re.MULTILINE)

    def execute(self):
        try:
            v = self.cli("debug hal show version")
        except self.CLISyntaxError:
            v = self.cli("debug hal show version slot 1")
        platform = self.rx_platform.search(v).group("platform")
        version = self.rx_version.search(v).group("version")
        return {
            "vendor": "Extreme",
            "platform": platform,
            "version": version
        }
