# -*- coding: utf-8 -*-
__author__ = "FeNikS"
# ---------------------------------------------------------------------
# Sencore.Probe.get_version
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
    name = "Sencore.Probe.get_version"
    interface = IGetVersion

    rx_version = re.compile(
        r"<software_version>(?P<data>.*?)</software_version>", re.MULTILINE | re.DOTALL
    )
    rx_platform = re.compile(r"<product>(?P<data>.*?)</product>", re.MULTILINE | re.DOTALL)

    def execute(self):
        platform = "Probe"
        version = "---"

        data = self.http.get("/probe/status")
        if data:
            match = self.rx_version.search(data)
            if match:
                version = match.group("data")

            match = self.rx_platform.search(data)
            if match:
                platform = match.group("data")

        return {"vendor": "Sencore", "platform": platform, "version": version}
