# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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

    rx_ver = re.compile(r"^software v\.(?P<version>\S+) ", re.MULTILINE)

    def execute(self):
        match = self.rx_ver.search(self.cli("version", cached=True))
        return {
            "vendor": "Alstec",
            "platform": "MSPU",
            "version": match.group("version")
        }
