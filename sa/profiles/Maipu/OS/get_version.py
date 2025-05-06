# ---------------------------------------------------------------------
# Maipu.OS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
tested on:
Maipu SM3220-28TF(E1)
Maipu NSS3530-30TXF(V1)
"""

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Maipu.OS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver1 = re.compile(
        r"(?P<platform>[^ ,]+) Device.*\n"
        r"\s+Software Version V(?P<version>[^ ,]+)\n"
        r"\s+BootRom Version (?P<bootrom>[^ ,]+)\n"
        r"\s+Hardware Version (?P<hwversion>[^ ,]+)\n"
        r"\s+CPLD Version (?P<cpldversion>[^ ,]+)\n"
        r"\s*Serial No.: (?P<serial>[^ ,]+)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    rx_ver2 = re.compile(
        r"\s*Hardware Model\s+:\s+(?P<platform>[^ ,]+)\n"
        r"\s*Hardware Version\s+:\s+(?P<hwversion>.+)\n"
        r"\s*MPU CPLD Version\s+:\s+(?P<cpldversion>[^ ,]+)\n"
        r"\s*Bootloader Version\s+:\s+(?P<bootrom>[^ ,]+)\n"
        r"\s*Software Version\s+:\s+(?P<version>[^ ,]+)\n"
        r"(\s*Serial No.: (?P<serial>[^ ,]+)\n)?",
        re.IGNORECASE,
    )

    def execute(self):
        v = self.cli("show version", cached=True)
        regexp = self.find_re([self.rx_ver1, self.rx_ver2], v)

        match = self.re_search(regexp, v)

        res = {
            "vendor": "Maipu",
            "version": match.group("version"),
            "platform": match.group("platform"),
            "attributes": {
                "Boot PROM": match.group("bootrom"),
                "HW version": match.group("hwversion"),
                "cpldversion": match.group("cpldversion"),
            },
        }

        serial = match.group("serial")
        if not serial:
            v = self.cli("show system module brief")
            for m in self.profile.rx_module_info.finditer(v):
                if m.group("module_name") == "Mpu 0":
                    serial = m.group("serial")

        if serial:
            res["attributes"]["Serial Number"] = serial

        return res
