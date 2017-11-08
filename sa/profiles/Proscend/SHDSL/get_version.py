# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Proscend.SHDSL.get_version
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
    name = "Proscend.SHDSL.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^\s*Chipset\s+:(?P<platform>\S+)\n", re.MULTILINE)
    rx_ver = re.compile(r"^\s*Firmware Version\s+:(?P<version>\S+)\n", re.MULTILINE)
    rx_hver = re.compile(r"^\s*Software Version\s+:(?P<hversion>\S+)\n", re.MULTILINE)
    rx_serial = re.compile(r"^\s*Serial No\s+:(?P<serial>\S+)\n", re.MULTILINE)

    def execute(self):
        ver = self.cli("show system", cached=True)
        match = self.re_search(self.rx_platform, ver)
        vmatch = self.re_search(self.rx_ver, ver)
        hmatch = self.re_search(self.rx_hver, ver)
        smatch = self.re_search(self.rx_serial, ver)
        return {
            "vendor": "Proscend",
            "platform": match.group("platform"),
            "version": vmatch.group("version"),
            "attributes": {
                "HW version": hmatch.group("hversion"),
                "Serial Number": smatch.group("serial")
            }
        }
