# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Terayon.BW.get_version
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
    name = "Terayon.BW.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^Terayon (?P<platform>\S+)\s+System", re.MULTILINE)
    rx_version = re.compile(r"^\s*BW Software Version: (?P<version>\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        platform = self.rx_platform.search(v).group("platform")
        version = self.rx_version.search(v).group("version")
        return {"vendor": "Terayon", "platform": platform, "version": version}
