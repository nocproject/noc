# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Carelink.SWG.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Carelink.SWG.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Software Version: (?P<platform>\S+) Ver:(?P<version>\S+)")

    def execute(self):
        match = self.rx_ver.search(self.cli("show system", cached=True))
        return {
            "vendor": "Carelink",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
