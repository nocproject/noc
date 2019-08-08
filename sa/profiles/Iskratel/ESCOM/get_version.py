# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^\s*SW version\s+(?P<version>\S+).*\n"
        r"^\s*Boot version\s+(?P<bootprom>\S+).*\n"
        r"^\s*HW version\s+(?P<hardware>\S+).*\n",
        re.MULTILINE,
    )
    rx_ver1 = re.compile(
        r"^\s+1\s+(?P<version>\S+)\s+(?P<bootprom>\S+)\s+(?P<hardware>\S+)", re.MULTILINE
    )
    rx_ver_escom_l = re.compile(
        r"SI3000 ESCOM L Series Software,\s*Version\s(?P<version>\S+) Build (?P<version_build>\S+),",
        re.MULTILINE,
    )
    rx_hw_escom_l = re.compile(
        r"ROM:\s*System Bootstrap, Version\s*(?P<bootprom>\S+),\s*hardware version:\s*(?P<hardware>\S+)\n"
        r"Serial num:(?P<serial>\S+), ID num:(?P<id_number>\S+)\n"
        r"System image file is \"(?P<image>\S+)\"",
        re.MULTILINE,
    )
    rx_platform = re.compile(r"^\s*System Description:\s+(?P<platform>.+)\n", re.MULTILINE)
    rx_platform1 = re.compile(r"^\s+1\s+(?P<platform>\S+)\s*\n", re.MULTILINE)
    rx_serial = re.compile(r"^\s*Serial number : (?P<serial>\S+)")

    def execute_cli(self, **kwargs):
        v = self.cli("show version", cached=True)
        for platform, ver in [
            ("ESCOM L", self.rx_ver_escom_l),
            ("ESCOM", self.rx_ver),
            ("ESCOM", self.rx_ver1),
        ]:
            match = ver.search(v)
            if match:
                break
        else:
            raise NotImplementedError
        if platform == "ESCOM L":
            hw_match = self.rx_hw_escom_l.search(v)
            return {
                "vendor": "Iskratel",
                "version": match.group("version"),
                "platform": platform,
                "image": hw_match.group("image"),
                "attributes": {
                    "Boot PROM": hw_match.group("bootprom"),
                    "HW version": hw_match.group("hardware"),
                    "Serial Number": hw_match.group("serial"),
                },
            }
        r = {
            "vendor": "Iskratel",
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware"),
            },
        }
        v = self.cli("show system", cached=True)
        match = self.rx_platform.search(v)
        if not match:
            match = self.rx_platform1.search(v)
        r["platform"] = match.group("platform")
        v = self.cli("show system id", cached=True)
        match = self.rx_serial.search(v)
        if match:
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
