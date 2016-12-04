# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alstec.24xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alstec.24xx.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^System Description\s+:\s+(?P<platform>\S+).+\n"
        r"^Bootloader\sVersion\s+:\s+(CFE |U-Boot )?(?P<bootprom>\S+)(\s\(.+\)|)\s*\n"
        r"^OS Version.+\n"
        r"^Software version\s+:\s+(?P<version>\S+)\s*\n"
        r"Software type\s+:\s+(?P<fwt>\S+)\s*\n",
        re.MULTILINE)
    rx_serial = re.compile("Serial Number\.+ (?P<serial>\S+)")

    def execute(self):
        v = self.cli("show sysinfo", cached=True)
        match = self.rx_ver.search(v)
        v = self.cli("show hardware", cached=True)
        match1 = self.rx_serial.search(v)
        return {
            "vendor": "Alstec",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "Firmware Type": match.group("fwt"),
                "Serial Number": match1.group("serial")
            }
        }
