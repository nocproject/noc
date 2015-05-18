# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "HP.1910.get_version"
    implements = [IGetVersion]
    cache = True

    rx_version_3Com = re.compile(
        r"^3Com Baseline Switch \S+ \S+ Software Version (?P<version>.+)$", re.MULTILINE)
    rx_version_HP = re.compile(
        r"^Comware Software, Version (?P<version>.+)$", re.MULTILINE)
    rx_bootprom = re.compile(
        r"^Bootrom Version is\s+(?P<bootprom>\S+)$", re.MULTILINE)
    rx_hardware = re.compile(
        r"^Hardware Version is (?P<hardware>\S+)$", re.MULTILINE)
    rx_platform_3Com = re.compile(
        r"^3Com Baseline Switch (?P<platform>\S+ \S+) Software Version (\S+ |)Release \S+$",
        re.MULTILINE)
    rx_platform_HP = re.compile(
        r"^HP (?P<platform>\S+) Switch$", re.MULTILINE)
    rx_platform_HP_snmp = re.compile(
        r"^HP (?P<platform>\S+) Switch Software Version Release \S+", re.MULTILINE)
    rx_serial = re.compile(
        r"^DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.1",
                                        cached=True)
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1",
                                        cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1",
                                         cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1",
                                       cached=True)
                platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.2.1",
                                        cached=True)
                match = self.rx_platform_HP_snmp.search(platform)
                if not match:
                    match = self.rx_platform_3Com.search(platform)
                platform = match.group("platform")
                return {
                        "vendor": vendor,
                        "platform": platform.replace(' ', '_'),
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
        plat = self.cli("display version", cached=True)
        match = self.rx_platform_HP.search(plat)
        if not match:
            vendor = "3Com"
            match = self.rx_platform_3Com.search(plat)
            version = self.rx_version_3Com.search(plat)
        else:
            vendor = "HP"
            version = self.rx_version_HP.search(plat)
        platform = match.group("platform")
        bootprom = self.rx_bootprom.search(plat)
        hardware = self.rx_hardware.search(plat)

        serial = self.cli("display device manuinfo", cached=True)
        serial = self.rx_serial.search(serial)

        return {
                "vendor": vendor,
                "platform": platform.replace(' ', '_'),
                "version": version.group("version"),
                "attributes": {
                    "Boot PROM": bootprom.group("bootprom"),
                    "HW version": hardware.group("hardware"),
                    "Serial Number": serial.group("serial")
                    }
                }
