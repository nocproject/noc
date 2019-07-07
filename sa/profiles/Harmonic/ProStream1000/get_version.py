__author__ = "FeNikS"
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# Harmonic.ProStream1000.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Harmonic.ProStream1000.get_version"
    interface = IGetVersion

    rx_version = re.compile(r" SwVersion=\"(?P<ver>.*?)\"", re.DOTALL | re.MULTILINE)

    def execute(self):
        version = ""
        data = self.scripts.get_config()
        match = self.rx_version.search(data)
        if match:
            version = match.group("ver")

        return {
            "vendor": "Harmonic",
            "platform": "ProStream 1000",
            "version": version if version else "Unknown",
        }
