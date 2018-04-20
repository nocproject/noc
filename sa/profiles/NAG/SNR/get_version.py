# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# NAG.SNR.get_version
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
    name = "NAG.SNR.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s+(?P<platform>\S+) Device, Compiled on.*\n"
        r"^\s+sysLocation.*\n"
        r"^\s+CPU Mac \S+\s*\n"
        r"^\s+Vlan MAC \S+\s*\n"
        r"^\s+SoftWare Version (?P<version>\S+)\s*\n"
        r"^\s+BootRom Version (?P<bootprom>\S+)\s*\n"
        r"^\s+HardWare Version (?P<hardware>\S+)\s*\n"
        r"^\s+CPLD Version.*\n"
        r"^\s+Serial No.:(?P<serial>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                vendor = self.snmp.get(
                    "1.3.6.1.2.1.47.1.1.1.1.12.1", cached=True)
                platform = self.snmp.get(
                    "1.3.6.1.2.1.1.1.0", cached=True)
                platform = platform.split(' ')[0]
                version = self.snmp.get(
                    "1.3.6.1.2.1.47.1.1.1.1.9.1", cached=True)
                bootprom = self.snmp.get(
                    "1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
                hardware = self.snmp.get(
                    "1.3.6.1.2.1.47.1.1.1.1.8.1", cached=True)
                serial = self.snmp.get(
                    "1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)
=======
##----------------------------------------------------------------------
## NAG.SNR.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "NAG.SNR.get_version"
    implements = [IGetVersion]
    cache = True

    def execute(self):
        # Try SNMP first
        print 1
        if self.snmp and self.access_profile.snmp_ro:
            try:
                vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.1",
                                        cached=True)
                platform = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                platform = platform.split(' ')[0]
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1",
                                        cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1",
                                         cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1",
                                       cached=True)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return {
                        "vendor": vendor,
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
<<<<<<< HEAD
        match = self.rx_ver.search(self.cli("show version", cached=True))
        return {
            "vendor": "NAG",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial")
            }
        }
=======
        raise Exception("Not implemented")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
