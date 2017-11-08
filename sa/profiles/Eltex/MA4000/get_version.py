# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_version
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
    name = "Eltex.MA4000.get_version"
    interface = IGetVersion
    cache = True

    rx_version = re.compile(
        r"^\s+Firmware version: (?P<version>\d+\S+)", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s+Serial number: (?P<serial>\S+)", re.MULTILINE)

    def execute(self):
        ver = self.cli("show system information 1", cached=True)
        if "Unit 1 is unavaible" in ver:
            ver = self.cli("show system information 2", cached=True)
        match = self.rx_version.search(ver)
        version = match.group("version")
        match = self.rx_serial.search(ver)
        serial = match.group("serial")

        return {
            "vendor": "Eltex",
            "platform": "MA4000",
            "version": version,
            "attributes": {
                "Serial Number": serial
            }
        }
