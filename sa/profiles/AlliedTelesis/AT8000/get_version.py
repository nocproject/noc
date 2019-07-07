# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^\s*Application Software Version\s*\.+ AT-S39 v(?P<version>\S+)\s*\n", re.MULTILINE
    )
    rx_platform = re.compile(
        r"^\s*Serial Number\s*\.+ (?P<serial>\S+)\s*\n"
        r"^\s*Model Name\s*\.+ (?P<platform>AT\S+)\s*\n",
        re.MULTILINE,
    )
    rx_bootprom = re.compile(
        r"^\s*Bootloader Version\s*\.+ \S+ v(?P<bootprom>\S+)\s*\n", re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show system")
        match = self.rx_platform.search(v)
        return {
            "vendor": "Allied Telesis",
            "platform": match.group("platform"),
            "version": self.rx_ver.search(v).group("version"),
            "attributes": {
                "Boot PROM": self.rx_bootprom.search(v).group("bootprom"),
                "Serial Number": match.group("serial"),
            },
        }
