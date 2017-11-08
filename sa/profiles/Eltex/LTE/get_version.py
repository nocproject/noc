# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.LTE.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(
        r"^Eltex LTE software version\s+(?P<version>\S+\s+build\s+\d+)")

    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.rx_version.search(ver)
        version = match.group("version")

        return {
            "vendor": "Eltex",
            "platform": "LTE",
            "version": version
        }
