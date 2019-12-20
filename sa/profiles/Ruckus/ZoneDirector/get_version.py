# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.ZoneDirector.get_version
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
    name = "Ruckus.ZoneDirector.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"\s*Version=\s+(?P<version>\S+).+\n", re.MULTILINE)
    rx_platform = re.compile(r"^\s*Model=\s+(?P<platform>\S+)\s*\n", re.MULTILINE)
    rx_serial = re.compile(r"^\s*Serial Number=\s+(?P<serial>\S+)\s*\n", re.MULTILINE)

    def execute(self):
        ver = self.cli("show sysinfo", cached=True)
        # print (ver)
        match = self.re_search(self.rx_ver, ver)
        pmatch = self.re_search(self.rx_platform, ver)
        smatch = self.re_search(self.rx_serial, ver)
        return {
            "vendor": "Ruckus",
            "platform": pmatch.group("platform"),
            "version": match.group("version"),
            "attributes": {"Serial Number": smatch.group("serial")},
        }
