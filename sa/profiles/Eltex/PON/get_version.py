# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Eltex.PON.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(
        r"^Device type:\s+(?P<platform>\S+).Hardware revision:\s+"
        r"(?P<hardware>\S+).Serial number:\s+(?P<serial>\S+)$",
        re.MULTILINE | re.DOTALL)

    rx_version = re.compile(
        r"^Eltex PON software version\s+(?P<version>\S+\s+build\s+\d+)")
    platforms = {
        "10": "PON-8X"
    }

    def execute(self):
        """
        # Try SNMP first
        if self.has_snmp():
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                platform = platform.split('.')[8]
                platform = self.platforms.get(platform.split(')')[0])
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992",
                                        cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67108992",
                                         cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992",
                                       cached=True)
                return {
                        "vendor": "Eltex",
                        "platform": platform,
                        "version": version,
                        "attributes": {
                            "Boot PROM": bootprom,
                            "HW version": hardware,
                            "Serial Number": serial
                            }
                        }
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        plat = self.cli("show factory settings", cached=True)
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
