# ---------------------------------------------------------------------
# NAG.SNR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
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
        r"(^\s+CPU M[Aa][Cc]\s+\S+\s*\n)?"
        r"(^\s+V[Ll][Aa][Nn] MAC\s+\S+\s*\n)?"
        r"^\s+Soft[Ww]are(?: Package)? Version\s+(?P<version>\S+)\s*\n"
        r"^\s+BootRom Version\s+(?P<bootprom>\S+)\s*\n"
        r"^\s+Hard[Ww]are Version\s+(?P<hardware>\S+)\s*\n"
        r"^\s+CPLD Version.*\n"
        r"^\s+(?:Serial No(?:\.\:)?|Device serial number)\s*(?P<serial>\S+)\s*\n",
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

    # For Version 2XXX
    rx_platform_ioss_v2 = re.compile(r"\s+(?P<platform>SNR-\S+)\s+")
    rx_ver_snmp_ioss_v2 = re.compile(r"Version (?P<version>\S+)\s+Build(?P<build>\d+)")
    rx_serial_snmp_ioss_v2 = re.compile(r"Serial num:(?P<serial>\S+)\s*,\s*ID num:\d+")

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
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
        try:
            vendor = self.snmp.get(mib["ENTITY-MIB::entPhysicalMfgName", 1])
            platform = v.split(" ")[0]
            vv = self.snmp.get(
                {
                    "version": mib["ENTITY-MIB::entPhysicalFirmwareRev", 1],
                    "bootprom": mib["ENTITY-MIB::entPhysicalSoftwareRev", 1],
                    "hardware": mib["ENTITY-MIB::entPhysicalHardwareRev", 1],
                    "serial": mib["ENTITY-MIB::entPhysicalSerialNum", 1],
                }
            )
            return {
                "vendor": vendor,
                "platform": platform,
                "version": vv["version"],
                "attributes": {
                    "Boot PROM": vv["bootprom"],
                    "HW version": vv["hardware"],
                    "Serial Number": vv["serial"],
                },
            }
        except (self.snmp.TimeOutError, self.snmp.SNMPError):
            self.logger.info("ENTITY-MIB not supported. Try next")
        match = self.rx_platform_ioss_v2.search(v)
        if match:
            platform = match.group("platform")
            match = self.rx_ver_snmp_ioss_v2.search(v)
            match_serial = self.rx_serial_snmp_ioss_v2.search(v)
            return {
                "vendor": "NAG",
                "platform": platform,
                "version": f"{match.group('version')}({match.group('build')})",
                "attributes": {"Serial Number": match_serial.group("serial")},
            }
        raise self.NotSupportedError("Unknown platform")
        # match = self.rx_ver_snmp.search(v)
        # if match:
        #     # Device do not support .1.3.6.1.2.1.47.x SNMP table
        #     return {
        #         "vendor": "FoxGate",
        #         "platform": match.group("platform"),
        #         "version": "unknown",  # I do not know right OID
        #     }

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver_snmp.search(v)
        vendor = "NAG"
        if not match:
            raise NotImplementedError("Not matched CLI")
        if match.group("vendor"):
            vendor = "FoxGate"
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
