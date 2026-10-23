# ---------------------------------------------------------------------
# Qtech.QSW.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Qtech.QSW.get_version"
    interface = IGetVersion
    cache = True
    always_prefer = "S"

    rx_plat_ver = re.compile(
        r"^software version\s+:\s*(QTECH|)\s+(?P<platform>\S+)\s+(?P<version>\S+)$", re.MULTILINE
    )
    rx_bootprom = re.compile(r"^bootrom version\s+:\s+V(?P<bootprom>\S*)$", re.MULTILINE)
    rx_hardware = re.compile(r"^hardware version\s+:\s+V(?P<hardware>\S+)$", re.MULTILINE)
    rx_serial = re.compile(r"^product serial number\s+:\s+(?P<serial>\S+)$", re.MULTILINE)

    rx_plat1 = re.compile(r"^\s+(?P<platform>QSW-\S+) Device, Compiled on", re.MULTILINE)
    rx_plat2 = re.compile(r"^\s+Device: (?P<platform>QSW-\S+), sysLocation:", re.MULTILINE)
    rx_soft1 = re.compile(r"^\s+SoftWare( Package)? Version (?P<version>\d\S+)$", re.MULTILINE)
    rx_bootprom1 = re.compile(r"^\s+BootRom Version (?P<bootprom>\d\S+)$", re.MULTILINE)
    rx_hardware1 = re.compile(r"^\s+HardWare Version (?P<hardware>.*?\S+)$", re.MULTILINE)
    rx_serial1 = re.compile(
        r"^\s+(?:Device serial number\s|Serial No\.:)(?P<serial>\d\S+)$", re.MULTILINE
    )

    def execute_snmp(self, **kwargs):
        platform = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.15.0", cached=True)
        if platform:
            if " " in platform:
                platform = platform.split(" ")[1]
            version = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.2.0", cached=True)
            version = version.split(" ")
            if platform == "Switch" and len(version) == 2:
                platform, version = version
            else:
                version = version[2]
            bootprom = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.9.0", cached=True)
            bootprom = bootprom.split("V")[1]
            hardware = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.8.0", cached=True)
            hardware = hardware.split("V")[1]
            serial = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.2.19.0", cached=True)
        else:
            platform = self.snmp.get("1.3.6.1.4.1.13464.1.2.1.1.2.15.0", cached=True)
            if " " in platform:
                platform = platform.split(" ")[1]
            version = self.snmp.get("1.3.6.1.4.1.13464.1.2.1.1.2.2.0", cached=True)
            version = version.split(" ")
            if platform == "Switch" and len(version) == 2:
                platform, version = version
            else:
                version = version[2]
            bootprom = self.snmp.get("1.3.6.1.4.1.13464.1.2.1.1.2.9.0", cached=True)
            if bootprom != "V":
                bootprom = bootprom.split("V")[1]
            else:
                bootprom = ""
            hardware = self.snmp.get("1.3.6.1.4.1.13464.1.2.1.1.2.8.0", cached=True)
            hardware = hardware.split("V")[1]
            serial = self.snmp.get("1.3.6.1.4.1.13464.1.2.1.1.2.19.0", cached=True)
        return {
            "vendor": "Qtech",
            "platform": platform,
            "version": version,
            "attributes": {"Boot PROM": bootprom, "HW version": hardware, "Serial Number": serial},
        }

    def execute_cli(self, **kwargs):
        # Fallback to CLI
        ver = self.cli("show version", cached=True)
        match = self.rx_plat_ver.search(ver)
        if match:
            platform = match.group("platform")
            version = match.group("version")
            bootprom = self.rx_bootprom.search(ver)
            hardware = self.rx_hardware.search(ver)
            serial = self.rx_serial.search(ver)
        else:
            match = self.rx_plat1.search(ver)
            if not match:
                match = self.rx_plat2.search(ver)
            platform = match.group("platform")
            version = self.rx_soft1.search(ver).group("version")
            bootprom = self.rx_bootprom1.search(ver)
            hardware = self.rx_hardware1.search(ver)
            serial = self.rx_serial1.search(ver)
        return {
            "vendor": "Qtech",
            "platform": platform,
            "version": version,
            "attributes": {
                "Boot PROM": bootprom.group("bootprom").strip(),
                "HW version": hardware.group("hardware").strip(),
                "Serial Number": serial.group("serial").strip(),
            },
        }
