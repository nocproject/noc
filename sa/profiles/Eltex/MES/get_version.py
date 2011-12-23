# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Eltex.MES.get_version"
    implements = [IGetVersion]
    cache = True

    rx_version = re.compile(
        r"^SW version+\s+(?P<version>\S+)", re.MULTILINE)
    rx_bootprom = re.compile(
        r"^Boot version+\s+(?P<bootprom>\S+)", re.MULTILINE)
    rx_hardware = re.compile(
        r"^HW version+\s+(?P<hardware>\S+)$", re.MULTILINE)

    rx_serial = re.compile(
        r"^Serial number :\s+(?P<serial>\S+)$", re.MULTILINE)
    rx_platform = re.compile(
        r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)

    platforms = {
        "10": "MES-1024",
        "24": "MES-3124",
        "26": "MES-5148",
        "30": "MES-3124F",
        "35": "MES-3108",
        "36": "MES-3108F",
        "38": "MES-3116",
        "39": "MES-3116F",
        "40": "MES-3224",
        "41": "MES-3224F",
        "42": "MES-2124",
    }

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
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

        # Fallback to CLI
        plat = self.cli("show system", cached=True)
        match = self.re_search(self.rx_platform, plat)
        platform = match.group("platform")
        platform = platform.split(".")[8]
        platform = self.platforms.get(platform)

        ver = self.cli("show version", cached=True)
        version = self.re_search(self.rx_version, ver)
        bootprom = self.re_search(self.rx_bootprom, ver)
        hardware = self.re_search(self.rx_hardware, ver)

        serial = self.cli("show system id", cached=True)
        serial = self.re_search(self.rx_serial, serial)

        return {
                "vendor": "Eltex",
                "platform": platform,
                "version": version.group("version"),
                "attributes": {
                    "Boot PROM": bootprom.group("bootprom"),
                    "HW version": hardware.group("hardware"),
                    "Serial Number": serial.group("serial")
                    }
                }
