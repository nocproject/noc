__author__ = "FeNikS"
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# Harmonic.DiviComElectra.get_version
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
    name = "Harmonic.DiviComElectra.get_version"
    interface = IGetVersion

    rx_version = re.compile(r" CodeVersion=\"(?P<ver>.*?)\"", re.DOTALL | re.MULTILINE)

    def execute(self):
        version = ""
        try:
            data = self.scripts.get_config()
            match = self.rx_version.search(data)
            if match:
                version = match.group("ver")
        except Exception:
            pass

        return {
            "vendor": "Harmonic",
            "platform": "DiviComElectra",
            "version": version if version else "Unknown",
        }
