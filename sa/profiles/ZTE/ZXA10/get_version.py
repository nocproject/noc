# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXA10.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# re modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "ZTE.ZXA10.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(
        r"^System Description: (?P<platform>\S+) Version (?P<version>\S+) Software,", re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show system-group", cached=True)
        match = self.rx_version.search(v)
        return {
            "vendor": "ZTE",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
