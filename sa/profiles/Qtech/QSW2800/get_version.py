# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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
        r"^\s*(?:Device: )?(?P<platform>\S+)(?: Device|, sysLocation\:).+\n"
        r"^\s*SoftWare(?: Package)? Version\s+(?P<version>\S+(?:\(\S+\))?)\n"
        r"^\s*BootRom Version\s+(?P<bootprom>\S+)\n"
        r"^\s*HardWare Version\s+(?P<hardware>\S+).+"
        r"^\s*(?:Device serial number |Serial No.:)(?P<serial>\S+)\n",
        re.MULTILINE | re.DOTALL)

    rx_ver_snmp = re.compile(
        r"Device: (?P<platform>\S+)\n"
        r"\sSoftWare\sVersion\s(?P<version>\S+)\n"
        r"\sBootRom\sVersion\s(?P<bootprom>\S+)\n"
        r"\sHardWare\sVersion\s(?P<hardware>\S+)\n"
        r"\s+Serial No.:(?P<serial>\S+)",
        re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                ver = self.snmp.get("1.3.6.1.2.1.1.1.0")
                match = self.rx_ver_snmp.search(ver)
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
            except self.snmp.TimeOutError:
                pass

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
