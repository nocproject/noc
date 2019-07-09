# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_version
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
    name = "AlliedTelesis.AT8100.get_version"
    cache = True
    interface = IGetVersion

    rx_plat = re.compile(
        r"^Base\s+(?P<platform>AT-81\S+)\s+(?P<hardware>\S+)\s+(?P<serial>\S+)\s*\n", re.MULTILINE
    )
    rx_boot = re.compile(r"^Bootloader version\s+:\s+(?P<bootprom>\S+)\s*\n", re.MULTILINE)
    rx_version = re.compile(r"^Software version\s+:\s+(?P<version>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show system")
        match1 = self.rx_plat.search(v)
        match2 = self.rx_boot.search(v)
        match3 = self.rx_version.search(v)

        return {
            "vendor": "Allied Telesis",
            "platform": match1.group("platform"),
            "version": match3.group("version"),
            "attributes": {
                "Boot PROM": match2.group("bootprom"),
                "HW version": match1.group("hardware"),
                "Serial Number": match1.group("serial"),
            },
        }
