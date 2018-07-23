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

    def fix_platform(self, oid):
        if oid.startswith("."):
            oid = oid[1:]
        if oid == "1.3.6.1.4.1.6339.1.1.1.228":
            return "QSW-3450-28T-AC"
        raise self.NotSupportedError()

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
