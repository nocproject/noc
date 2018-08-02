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
from noc.core.mib import mib


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

    rx_vendor = re.compile(r"^DeviceOid\s+\d+\s+(?P<oid>\S+)", re.MULTILINE)

    qtech_platforms = {
        "1.3.6.1.4.1.6339.1.1.1.48": "QSW-2800",
        "1.3.6.1.4.1.6339.1.1.1.49": "QSW-2800",
        "1.3.6.1.4.1.6339.1.1.1.228": "QSW-3450-28T-AC",
        "1.3.6.1.4.1.6339.1.1.1.244": "S5750E-28X-SI-24F-D",
        "1.3.6.1.4.1.6339.1.1.2.40": "QSW-8300-52F",
        "1.3.6.1.4.1.6339.1.1.2.59": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.13464.1.3.13": "QSW-2900-24T",
        "1.3.6.1.4.1.13464.1.3.26.7": "QSW-2910",
        "1.3.6.1.4.1.27514": "QSW-8200–28F-AC-DC rev.Q1",
        "1.3.6.1.4.1.27514.1.1.1.39": "QSW-2800-26T-AC",
        "1.3.6.1.4.1.27514.1.1.1.48": "QSW-2800-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.49": "QSW-2800-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.52": "QSW-2800-28T-AC-RPS",
        "1.3.6.1.4.1.27514.1.1.1.53": "QSW-2800-28T-DC",
        "1.3.6.1.4.1.27514.1.1.1.220": "QSW-3400-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.221": "QSW-3400-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.234": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.1.235": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.1.248": "QSW-3450-28T-POE-AC",
        "1.3.6.1.4.1.27514.1.1.1.282": "QSW-3470-10T-AC",
        "1.3.6.1.4.1.27514.1.1.1.310": "QSW-3580-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.337": "QSW-2850-28T-AC",
        "1.3.6.1.4.1.27514.1.1.1.354": "QSW-3470-28T-AC-POE",
        "1.3.6.1.4.1.27514.1.1.1.356": "QSW-3470-10T-AC-POE",
        "1.3.6.1.4.1.27514.1.1.1.339": "QSW-2850-18T-AC",
        "1.3.6.1.4.1.27514.1.1.1.351": "QSW-3500-10T-AC",
        "1.3.6.1.4.1.27514.1.1.2.39": "QSW-8200-28F",
        "1.3.6.1.4.1.27514.1.1.2.40": "QSW-8300",
        "1.3.6.1.4.1.27514.1.1.2.53": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.2.59": "QSW-8200-28F-AC-DC",
        "1.3.6.1.4.1.27514.1.1.2.60": "QSW-8270-28F-AC",
        "1.3.6.1.4.1.27514.1.3.13": "QSW-2900-24T",
        "1.3.6.1.4.1.27514.1.3.13.0": "QSW-2900",
        "1.3.6.1.4.1.27514.1.3.26.2": "QSW-3900",
        "1.3.6.1.4.1.27514.1.3.26.1": "QSW-3900",
        "1.3.6.1.4.1.27514.1.3.25.2": "QSW-2900-24T4",
        "1.3.6.1.4.1.27514.1.3.26.7": "QSW-2910-28F",
        "1.3.6.1.4.1.27514.1.3.26.8": "QSW-2910-28T-POE",
        "1.3.6.1.4.1.27514.1.3.26.9": "QSW-2910-10T-POE",
        "1.3.6.1.4.1.27514.1.3.32.1": "QSW-2910-26T",
        "1.3.6.1.4.1.27514.1.3.32.3": "QSW-2910-09T-POE",
        "1.3.6.1.4.1.27514.1.280": "QSW-2870-10T",
        "1.3.6.1.4.1.27514.1.287": "QSW-2870-28T",
        "1.3.6.1.4.1.27514.1.282803": "QSW-2800-28T",
        "1.3.6.1.4.1.27514.3.2.10": "QSW-3470-10T",
        "1.3.6.1.4.1.27514.6.55": "QSW-2500E",
        "1.3.6.1.4.1.27514.101": "QFC-PBIC",
        "1.3.6.1.4.1.27514.102.1.2.40": "QSW-8300-52F"
    }

    def fix_platform(self, oid):
        if oid.startswith("."):
            oid = oid[1:]
        platform = self.qtech_platforms.get(oid)
        if platform is None:
            raise self.NotSupportedError("Unknown platform OID: %s" % oid)
        return platform

    def execute_snmp(self, **kwargs):
        try:
            ver = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"], cached=True)
            match = self.rx_ver.search(ver)
            match2 = self.rx_ver2.search(ver)
            if match:
                platform = match.group("platform").strip(" ,")
                version = match.group("version")
                bootprom = match.group("bootprom")
                hardware = match.group("hardware")
                serial = match.group("serial")
                if platform == "Switch":
                    oid = self.snmp.get(mib["SNMPv2-MIB::sysObjectID.0"])
                    platform = self.fix_platform(oid)

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
                version = match2.group("version")
                bootprom = match2.group("bootprom")
                hardware = match2.group("hardware")
                serial = match2.group("serial")
                oid = self.snmp.get(mib["SNMPv2-MIB::sysObjectID.0"])
                platform = self.fix_platform(oid)
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
            raise self.NotSupportedError

    def execute_cli(self, **kwargs):
        ver = self.cli("show version", cached=True)
        match = self.rx_ver.search(ver)
        if match:
            platform = match.group("platform").strip(" ,")
            version = match.group("version")
            bootprom = match.group("bootprom")
            hardware = match.group("hardware")
            serial = match.group("serial")
            if platform == "Switch":
                try:
                    # Hidden command !!!
                    v = self.cli("show vendor")
                    match = self.rx_vendor.search(v)
                    if match:
                        platform = self.fix_platform(match.group("oid"))
                except self.CLISyntaxError:
                    pass

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
