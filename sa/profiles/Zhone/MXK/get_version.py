# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.MXK.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Zhone.MXK.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"software version MXK (?P<version>\S+)")
    rx_platform = re.compile(r"^(?P<platform>MXK \d+)\s*\n", re.MULTILINE)

    def execute(self):
        v = self.cli("swversion", cached=True)
        match = self.re_search(self.rx_ver, v)
        version = match.group("version")
        v = self.cli("slots", cached=True)
        match = self.re_search(self.rx_platform, v)
        platform = match.group("platform")
        return {
            "vendor": "Zhone",
            "version": version,
            "platform": platform
        }
