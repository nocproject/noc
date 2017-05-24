# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.DSLAM.get_version
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
    name = "Eltex.DSLAM.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(r"version:\s+(?P<version>\S+)")

    def execute(self):
        try:
            ver = self.cli("system show software info", cached=True)
        except self.CLISyntaxError:
            ver = self.cli("system show software version", cached=True)
        match = self.rx_version.search(ver)
        if match:
            return {
                "vendor": "Eltex",
                "platform": "DSLAM",
                "version": match.group("version")
            }
        else:
            return {
                "vendor": "Eltex",
                "platform": "DSLAM",
                "version": "UNKNOWN"
            }
