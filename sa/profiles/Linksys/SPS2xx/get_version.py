# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Linksys.SPS2xx.get_version"
    implements = [IGetVersion]
    cache = True

    rx_version = re.compile(r"^SW version\s+(?P<version>\S+)\s+\(.+\)$",
                            re.MULTILINE)
    rx_bootprom = re.compile(r"^Boot version\s+(?P<bootprom>\S+)\s+\(.+\)$",
                             re.MULTILINE)
    rx_hardware = re.compile(r"^HW version\s+(?P<hardware>\S+)\s+\(.+\)$",
                             re.MULTILINE)

    rx_serial = re.compile(r"^System Serial Number:\s+(?P<serial>\S+)$",
                           re.MULTILINE)
    rx_platform = re.compile(r"^System Object ID:\s+(?P<platform>\S+)$",
                             re.MULTILINE)

    platforms = {
        "9.224.1": "SPS-224G4",
        "1.208.1": "SRW-208",
        "1.208.2": "SRW-208G",
        "1.2016.1": "SRW-2016",
        "1.2048.1": "SRW-2048",
        "3955.6.5048": "SRW-248G",
        }

    def execute(self):
        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                platform = platform.split('.')
                N = len(platform)
                platform = platform[N - 3] + '.' + platform[N - 2] + '.' \
                    + platform[N - 1]
                platform = self.platforms.get(platform.split(')')[0], '????')
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992",
                                        cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67108992",
                                         cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992",
                                       cached=True)
                return {
                    "vendor": "Linksys",
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
        platform = match.group("platform").split('.')
        N = len(platform)
        platform = platform[N - 3] + '.' + platform[N - 2] + '.' \
            + platform[N - 1]
        platform = self.platforms.get(platform.split(')')[0], '????')

        ver = self.cli("show version", cached=True)
        version = self.re_search(self.rx_version, ver)
        bootprom = self.re_search(self.rx_bootprom, ver)
        r = {
            "vendor": "Linksys",
            "platform": platform,
            "version": version.group("version"),
            "attributes": {
                "Boot PROM": bootprom.group("bootprom"),
                }
        }
        hardware = self.rx_hardware.search(ver)
        if hardware:
            r["attributes"]["HW version"] = hardware.group("hardware")
        serial = self.rx_serial.search(plat)
        if serial:
            r["attributes"]["Serial Number"] = serial.group("serial")
        return r
