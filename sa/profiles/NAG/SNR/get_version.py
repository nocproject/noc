# ---------------------------------------------------------------------
# NAG.SNR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
        r"^\s+(?:(?P<vendor>FoxGate) )?(?P<platform>\S+) Device, Compiled on.*\n"
        r"(^\s+sysLocation.*\n)?"
        r"(^\s+CPU Mac \S+\s*\n)?"
        r"(^\s+Vlan MAC \S+\s*\n)?"
        r"^\s+Soft[Ww]are(?: Package)? Version (?P<version>\S+)\s*\n"
        r"^\s+BootRom Version (?P<bootprom>\S+)\s*\n"
        r"^\s+Hard[Ww]are Version (?P<hardware>\S+)\s*\n"
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
    rx_ver_snmp2 = re.compile(r"^(?P<vendor>FoxGate) (?P<platform>\S+)$", re.MULTILINE)

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
        match = self.rx_ver_snmp.search(v)
        if match:
            return {
                "vendor": "NAG",  # Need more examples for other vendors
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {
                    "Boot PROM": match.group("bootprom"),
                    "HW version": match.group("hardware"),
                    "Serial Number": match.group("serial"),
                },
            }
        else:
            match = self.rx_ver_snmp.search(v)
            if match:
                # Device do not support .1.3.6.1.2.1.47.x SNMP table
                return {
                    "vendor": "FoxGate",
                    "platform": match.group("platform"),
                    "version": "unknown",  # I do not know right OID
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
        if match.group("vendor"):
            vendor = "FoxGate"
        else:
            vendor = "NAG"
        return {
            "vendor": vendor,
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
                "Serial Number": match.group("serial"),
            },
        }
