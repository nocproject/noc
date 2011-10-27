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

rx_version = re.compile(r"^SW version+\s+(?P<version>\S+)", re.MULTILINE)
rx_bootprom = re.compile(r"^Boot version+\s+(?P<bootprom>\S+)", re.MULTILINE)
rx_hardware = re.compile(r"^HW version+\s+(?P<hardware>\S+)$", re.MULTILINE)

rx_serial = re.compile(r"^Serial number :\s+(?P<serial>\S+)$", re.MULTILINE)
rx_platform = re.compile(r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)

class Script(NOCScript):
    name = "Eltex.MES.get_version"
    implements = [IGetVersion]
    cache = True

    def execute(self):
        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                platform = 'MES3124F'
#                platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.XXX.67108992", cached=True)
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992", cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67108992", cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992", cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992", cached=True)
                return {
                        "vendor"     : "Eltex",
                        "platform"   : platform,
                        "version"    : version,
                        "attributes" : {
                                        "Boot PROM"     : bootprom,
                                        "HW version"    : hardware,
                                        "Serial Number" : serial
                                        }
                        }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        plat = self.cli("show system", cached=True)
        match = self.re_search(rx_platform, plat)
        platform = match.group("platform")
        platform = platform.split('.')[8]
        if platform == '24':
            platform = 'MES-3124'
        elif platform == '26':
            platform = 'MES-5148'
        elif platform == '30':
            platform = 'MES-3124F'
        elif platform == '35':
            platform = 'MES-3108'
        elif platform == '36':
            platform = 'MES-3108F'
        elif platform == '38':
            platform = 'MES-3116'
        elif platform == '39':
            platform = 'MES-3116F'
        elif platform == '40':
            platform = 'MES-3224'
        elif platform == '41':
            platform = 'MES-3224F'

        ver = self.cli("show version", cached=True)
        version = self.re_search(rx_version, ver)
        bootprom = self.re_search(rx_bootprom, ver)
        hardware = self.re_search(rx_hardware, ver)

        serial = self.cli("show system id", cached=True)
        serial = self.re_search(rx_serial, serial)

        return {
                "vendor"     : "Eltex",
                "platform"   : platform,
                "version"    : version.group("version"),
                "attributes" : {
                                "Boot PROM"     : bootprom.group("bootprom"),
                                "HW version"    : hardware.group("hardware"),
                                "Serial Number" : serial.group("serial")
                                }
                }
