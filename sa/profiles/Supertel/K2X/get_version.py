# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_version
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
    name = "Supertel.K2X.get_version"
    implements = [IGetVersion]
    cache = True

    rx_version = re.compile(
        r"^SW version\s+(?P<version>\S+)", re.MULTILINE)
    rx_bootprom = re.compile(
        r"^Boot version\s+(?P<bootprom>\S+)", re.MULTILINE)
    rx_hardware = re.compile(
        r"^HW version\s+(?P<hardware>\S+)$", re.MULTILINE)

    rx_serial = re.compile(
        r"^Serial number\s*:\s*(?P<serial>\S+)$", re.MULTILINE)
    rx_platform = re.compile(
        r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                platform = self.profile.platforms[platform.split('.')[8]]
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992",
                                        cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67108992",
                                         cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992",
                                       cached=True)
                return {
                    "vendor": "Supertel",
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

        # Fallback to CLI
        plat = self.cli("show system", cached=True)
        match = self.rx_platform.search(plat)
        platform = match.group("platform")
        platform = self.profile.platforms[platform.split('.')[8]]

        ver = self.cli("show version", cached=True)
        version = self.rx_version.search(ver)
        bootprom = self.rx_bootprom.search(ver)
        hardware = self.rx_hardware.search(ver)

        serial = self.cli("show system id", cached=True)
        serial = self.rx_serial.search(serial)

        return {
            "vendor": "Supertel",
            "platform": platform,
            "version": version.group("version"),
            "attributes": {
                "Boot PROM": bootprom.group("bootprom"),
                "HW version": hardware.group("hardware"),
                "Serial Number": serial.group("serial")
                }
            }
