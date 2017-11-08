# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_version
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
    name = "Eltex.LTP.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(
        r"^\s*TYPE:\s+(?P<platform>\S+)\s*\n"
        r"^\s*HW_revision:\s+(?P<hardware>\S+)\s*\n"
        r"^\s*SN:\s+(?P<serial>\S+)",
        re.MULTILINE)

    rx_version = re.compile(
        r"^Eltex \S+ software version\s+(?P<version>\S+\s+build\s+\d+)")

    def execute(self):
        plat = self.cli("show system environment", cached=True)
        match = self.rx_platform.search(plat)
        platform = match.group("platform")
        hardware = match.group("hardware")
        serial = match.group("serial")

        ver = self.cli("show version", cached=True)
        match = self.rx_version.search(ver)
        version = match.group("version")

        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version,
            "attributes": {
                "HW version": hardware,
                "Serial Number": serial
            }
        }
