# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^(?P<platform>\S+) Ethernet Managed Switch\n"
        r"(^eNOS software, Compiled on .*\n)?"
        r"(^Copyright .*\n)?"
        r"(^All rights reserved\n)?"
        r"(^CPU Mac \S+\s*\n)?"
        r"(^Vlan MAC \S+\s*\n)?"
        r"^Soft[Ww]are Version (?P<version>\S+)\s*\n"
        r"^BootRom Version (?P<bootprom>\S+).*\n"
        r"^Hard[Ww]are Version (?P<hardware>\S+)*\n"
        r"^CPLD Version.*\n"
        r"^Serial No.: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )
    # rx_ver_snmp = re.compile(
    #     r"(?P<platform>\S+) Ethernet Managed Switch\n"
    #     r"SoftWare Version (?P<version>\S+)\s*\n"
    #     r"BootRom Version (?P<bootprom>\S+)\s*\n"
    #     r"HardWare Version (?P<hardware>\S+)\s*\n"
    #     r"(?:Serial No.:|Device serial number)\s*(?P<serial>\S+)\s*\n",
    #     re.MULTILINE,
    # )
    # rx_ver_snmp2 = re.compile(r"^(?P<vendor>FoxGate) (?P<platform>\S+)$", re.MULTILINE)

    # def execute_snmp(self):
    #     v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
    #     match = self.rx_ver_snmp.search(v)
    #     if match:
    #         return {
    #             "vendor": "NAG",  # Need more examples for other vendors
    #             "platform": match.group("platform"),
    #             "version": match.group("version"),
    #             "attributes": {
    #                 "Boot PROM": match.group("bootprom"),
    #                 "HW version": match.group("hardware"),
    #                 "Serial Number": match.group("serial"),
    #             },
    #         }
    #     else:
    #         match = self.rx_ver_snmp.search(v)
    #         if match:
    #             # Device do not support .1.3.6.1.2.1.47.x SNMP table
    #             return {
    #                 "vendor": "FoxGate",
    #                 "platform": match.group("platform"),
    #                 "version": "unknown",  # I do not know right OID
    #             }
    #     vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.1", cached=True)
    #     platform = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
    #     platform = platform.split(" ")[0]
    #     version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1", cached=True)
    #     bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
    #     hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1", cached=True)
    #     serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)
    #     return {
    #         "vendor": vendor,
    #         "platform": platform,
    #         "version": version,
    #         "attributes": {"Boot PROM": bootprom, "HW version": hardware, "Serial Number": serial},
    #     }

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        print(match.group())
        #if not match:
        #    match = self.rx_ver_snmp.search(v)
        vendor = "NAG"
        #if match.group("vendor"):
        #    vendor = "FoxGate"
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
