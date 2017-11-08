# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_version
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
    name = "Eltex.MES5448.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(
        r"^Machine Model\.+ (?P<platform>\S+)\s*\n"
        r"^Serial Number\.+ (?P<serial>\S+)\s*\n"
        r"^Maintenance Level\.+ \S+\s*\n"
        r"^Manufacturer\.+ \S+\s*\n"
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\s*\n"
        r"^Software Version\.+ (?P<version>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.rx_version.search(ver)
        r = {
            "vendor": "Eltex",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Serial Number": match.group("serial")
            }
        }
        return r
