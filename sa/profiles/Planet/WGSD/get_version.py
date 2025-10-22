# ---------------------------------------------------------------------
# Planet.WGSD.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Planet.WGSD.get_version"
    interface = IGetVersion
    cache = True

    rx_version1 = re.compile(r"^SW version+\s+(?P<version>\S+)", re.MULTILINE)
    rx_version2 = re.compile(r"^Active-image: \S+\s*\n^\s+Version: (?P<version>\S+)", re.MULTILINE)
    rx_bootprom = re.compile(r"^Boot version+\s+(?P<bootprom>\S+)", re.MULTILINE)
    rx_hardware = re.compile(r"^HW version+\s+(?P<hardware>\S+)$", re.MULTILINE)

    rx_serial1 = re.compile(r"^Serial number :\s+(?P<serial>\S+)$", re.MULTILINE)
    rx_serial2 = re.compile(r"^\s+1\s+(?P<serial>\S+)\s*\n", re.MULTILINE)
    rx_platform = re.compile(r"^System Object ID:\s+(?P<platform>\S+)$", re.MULTILINE)

    platforms = {"1466": "WGSD-1022", "89": "WGSD-1022", "89.1.1": "WGSD-1022"}

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                platform = self.snmp.get("1.3.6.1.2.1.1.2.0", cached=True)
                platform = platform.split(".")[-1]
                platform = self.platforms.get(platform.split(")")[0])
                version = self.snmp.get("1.3.6.1.4.1.89.2.4.0", cached=True)
                bootprom = self.snmp.get("1.3.6.1.4.1.89.2.10.0", cached=True)
                hardware = self.snmp.get("1.3.6.1.4.1.89.2.11.1.0", cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992", cached=True)
                return {
                    "vendor": "Planet",
                    "platform": platform,
                    "version": version,
                    "attributes": {
                        "Boot PROM": bootprom,
                        "HW version": hardware,
                        "Serial Number": serial,
                    },
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        stacked = False
        plat = self.cli("show system", cached=True)
        match = self.rx_platform.search(plat)
        if not match:
            plat = self.cli("show system unit 1", cached=True)
            stacked = True
        match = self.re_search(self.rx_platform, plat)
        platform = match.group("platform")
        platform = platform.split(".")[8]
        platform = self.platforms.get(platform)

        if stacked:
            ver = self.cli("show version unit 1", cached=True)
        else:
            ver = self.cli("show version", cached=True)
        match = self.rx_version1.search(ver)
        if match:
            version = self.re_search(self.rx_version1, ver)
            bootprom = self.re_search(self.rx_bootprom, ver)
            hardware = self.re_search(self.rx_hardware, ver)
        else:
            version = self.rx_version2.search(ver)
            bootprom = None
            hardware = None

        if stacked:
            ser = self.cli("show system id unit 1", cached=True)
        else:
            ser = self.cli("show system id", cached=True)
        try:
            match = self.rx_serial1.search(ser)
            if match:
                s = self.re_search(self.rx_serial1, ser)
                serial = s.group("serial")
            else:
                s = self.re_search(self.rx_serial2, ser)
                serial = s.group("serial")
        except Exception:
            serial = None
        r = {
            "vendor": "Planet",
            "platform": platform,
            "version": version.group("version"),
            "attributes": {"Serial Number": serial},
        }
        if bootprom:
            r["attributes"]["Boot PROM"] = bootprom.group("bootprom")
            r["attributes"]["HW version"] = hardware.group("hardware")
        return r
