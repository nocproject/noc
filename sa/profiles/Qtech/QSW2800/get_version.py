# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.QSW2800.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s*(?:Device: )?(?P<platform>\S+)(?: Device|, sysLocation\:|).*\n"
        r"^\s*SoftWare(?: Package)? Version\s+(?P<version>\S+(?:\(\S+\))?)\n"
        r"^\s*BootRom Version\s+(?P<bootprom>\S+)\n"
        r"^\s*HardWare Version\s+(?P<hardware>\S+).+"
        r"^\s*(?:Device serial number |Serial No.:(?:|\s))(?P<serial>\S+)\n",
        re.MULTILINE | re.DOTALL)

    rx_ver2 = re.compile(
        r"^\s*SoftWare(?: Package)? Version\s+(?P<version>\S+(?:\(\S+\))?)\n"
        r"^\s*BootRom Version\s+(?P<bootprom>\S+)\n"
        r"^\s*HardWare Version\s+(?P<hardware>\S+).+"
        r"^\s*(?:Device serial number |Serial No.:(?:|\s))(?P<serial>\S+)\n",
        re.MULTILINE | re.DOTALL)

    def execute_snmp(self, **kwargs):
        try:
            ver = self.snmp.get("1.3.6.1.2.1.1.1.0")
            match = self.rx_ver.search(ver)
            match2 = self.rx_ver2.search(ver)
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
            elif match2:
                version = match.group("version")
                bootprom = match.group("bootprom")
                hardware = match.group("hardware")
                serial = match.group("serial")
                return {
                    "vendor": "Qtech",
                    "platform": "Unknown",
                    "version": version,
                    "attributes": {
                        "Boot PROM": bootprom,
                        "HW version": hardware,
                        "Serial Number": serial
                    }
                }
            else:
                return {
                    "vendor": "Qtech",
                    "platform": "Unknown",
                    "version": "Unknown"
                }
        except self.snmp.TimeOutError:
            raise self.NotSupportedError

    def execute_cli(self, **kwargs):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.search(ver)
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
                "vendor": "Qtech",
                "platform": "Unknown",
                "version": "Unknown"
            }
