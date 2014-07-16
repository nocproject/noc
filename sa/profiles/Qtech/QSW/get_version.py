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
    name = "Qtech.QSW.get_version"
    implements = [IGetVersion]
    cache = True

    rx_plat_ver = re.compile(
        r"^software version\s+:\s+QTECH\s+(?P<platform>\S+)\s+"
        r"(?P<version>\S+)$", re.MULTILINE)
    rx_bootprom = re.compile(
        r"^bootrom version\s+:\s+V+(?P<bootprom>\S+)$", re.MULTILINE)
    rx_hardware = re.compile(
        r"^hardware version\s+:\s+V+(?P<hardware>\S+)$", re.MULTILINE)
    rx_serial = re.compile(
        r"^product serial number\s+:\s+(?P<serial>\S+)$", re.MULTILINE)

    rx_plat1 = re.compile(
        r"^\s+(?P<platform>QSW-\S+) Device, Compiled on", re.MULTILINE)
    rx_soft1 = re.compile(
        r"^\s+SoftWare( Package)? Version (?P<version>\d\S+)$", re.MULTILINE)
    rx_bootprom1 = re.compile(
        r"^\s+BootRom Version (?P<bootprom>\d\S+)$", re.MULTILINE)
    rx_hardware1 = re.compile(
        r"^\s+HardWare Version (?P<hardware>\d\S+)$", re.MULTILINE)
    rx_serial1 = re.compile(
        r"^\s+(?:Device serial number\s|Serial No\.:)(?P<serial>\d\S+)$",
        re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                platform = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.15.0",
                                        cached=True)
                if platform == '':
                    raise self.snmp.TimeOutError
                platform = platform.split(' ')[1]
                version = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.2.0",
                                        cached=True)
                version = version.split(' ')[2]
                bootprom = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.9.0",
                                         cached=True)
                bootprom = bootprom.split('V')[1]
                hardware = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.8.0",
                                         cached=True)
                hardware = hardware.split('V')[1]
                serial = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.19.0",
                                       cached=True)
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
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        ver = self.cli("show version", cached=True)
        match = self.rx_plat_ver.search(ver)
        if match:
            platform = match.group("platform")
            version = match.group("version")
            bootprom = self.re_search(self.rx_bootprom, ver)
            hardware = self.re_search(self.rx_hardware, ver)
            serial = self.re_search(self.rx_serial, ver)
        else:
            platform = self.re_search(self.rx_plat1, ver).group("platform")
            version = self.re_search(self.rx_soft1, ver).group("version")
            bootprom = self.re_search(self.rx_bootprom1, ver)
            hardware = self.re_search(self.rx_hardware1, ver)
            serial = self.re_search(self.rx_serial1, ver)

        return {
                "vendor": "Qtech",
                "platform": platform,
                "version": version,
                "attributes": {
                    "Boot PROM": bootprom.group("bootprom"),
                    "HW version": hardware.group("hardware"),
                    "Serial Number": serial.group("serial")
                    }
                }
