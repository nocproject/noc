# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Qtech.QSW2800.get_version"
    implements = [IGetVersion]
    cache = True

    rx_ver = re.compile(r"^\s*(?P<platform>\S+) Device.+"
        r"\s*SoftWare Version (?P<version>\S+)."
        r"\s*BootRom Version (?P<bootprom>\S+).+"
        r"\s*HardWare Version (?P<hardware>\S+).+"
        r"\s*Device serial number (?P<serial>\S+).",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.match(ver)
        if match:
            platform = match.group("platform")
            version = match.group("version")
            bootprom = match.group("bootprom")
            hardware = match.group("hardware")
            serial = match.group("serial")

            return {
                    "vendor": "Qtech",
                    "platform": platform,
                    "version": version,
                    "attributes": {
                        "Boot PROM": bootprom,
                        "HW version": hardware,
                        "Serial Number": serial
                    }
            }
        else:
            return {
                "vendor": "Unknown",
                "platform": "Unknown",
                "version": "Unknown"
            }
