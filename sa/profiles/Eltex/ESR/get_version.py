# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_version
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
    name = "Eltex.ESR.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"System type:\s+Eltex\s+(?P<platform>\S+)\s+.+\n"
        r"System name:\s+\S+\s*\n"
        r"Software version:\s+(?P<version>\S+)\s+.+\n"
        r"Hardware version:\s+(?P<hardware>\S+)\s*\n"
        r"System uptime:.+\n"
        r"System MAC address:\s+\S+\s*\n"
        r"System serial number:\s+(?P<serial>\S+)\s*\n")

    def execute(self):
        c = self.scripts.get_system()
        match = self.rx_ver.search(c)
        return {
            "vendor": "Eltex",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial")
            }
        }
