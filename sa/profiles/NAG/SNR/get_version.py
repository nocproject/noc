# ---------------------------------------------------------------------
# NAG.SNR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "NAG.SNR.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s+(?P<platform>\S+) Device, Compiled on.*\n"
        r"(^\s+sysLocation.*\n)?"
        r"(^\s+CPU Mac \S+\s*\n)?"
        r"(^\s+Vlan MAC \S+\s*\n)?"
        r"^\s+SoftWare(?: Package)? Version (?P<version>\S+)\s*\n"
        r"^\s+BootRom Version (?P<bootprom>\S+)\s*\n"
        r"^\s+HardWare Version (?P<hardware>\S+)\s*\n"
        r"^\s+CPLD Version.*\n"
        r"^\s+(?:Serial No.:|Device serial number)\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_ver_snmp = re.compile(
        r"^\s*(?P<platform>\S+) Device, Compiled.*\n"
        r"^\s+SoftWare Version (?P<version>\S+)\s*\n"
        r"^\s+BootRom Version (?P<bootprom>\S+)\s*\n"
        r"^\s+HardWare Version (?P<hardware>\S+)\s*\n"
        r"^\s+(?:Serial No.:|Device serial number)\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_snmp(self):
        match = self.rx_ver_snmp.search(self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True))
        if match:
            return {
                "vendor": "NAG",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {
                    "Boot PROM": match.group("bootprom"),
                    "HW version": match.group("hardware"),
                    "Serial Number": match.group("serial"),
                },
            }
        vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.1", cached=True)
        platform = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        platform = platform.split(" ")[0]
        version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1", cached=True)
        bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
        hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1", cached=True)
        serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)
        return {
            "vendor": vendor,
            "platform": platform,
            "version": version,
            "attributes": {"Boot PROM": bootprom, "HW version": hardware, "Serial Number": serial},
        }

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver_snmp.search(v)
        return {
            "vendor": "NAG",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }
