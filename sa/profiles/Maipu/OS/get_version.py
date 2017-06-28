# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Maipu.OS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
test on Maipu SM3220-28TF(E1)


"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

class Script(BaseScript):
    name = "Maipu.OS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"(?P<platform>[^ ,]+) Device.*\n"
        r"\s+Software Version V(?P<version>[^ ,]+)\n"
        r"\s+BootRom Version (?P<bootrom>[^ ,]+)\n"
        r"\s+Hardware Version (?P<hwversion>[^ ,]+)\n"
        r"\s+CPLD Version (?P<cpldversion>[^ ,]+)\n"
        r"\s*Serial No.: (?P<serial>[^ ,]+)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self):
        v = ""
        v = self.cli("show version", cached=True)
        rx = self.find_re([self.rx_ver], v)

        match = self.re_search(self.rx_ver, v)

        return {
            "vendor": "Maipu",
            "version": match.group("version"),
            "platform": match.group("platform"),
            "attributes": {
                "Boot PROM": match.group("bootrom"),
                "HW version": match.group("hwversion"),
                "Serial Number" : match.group("serial"),
                "cpldversion": match.group("cpldversion")
            }
        }

