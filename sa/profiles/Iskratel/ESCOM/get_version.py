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
        r"^\s*HW version\s+(?P<hardware>\S+).*\n", re.MULTILINE)
    rx_ver1 = re.compile(
        r"^\s+1\s+(?P<version>\S+)\s+(?P<bootprom>\S+)\s+(?P<hardware>\S+)",
        re.MULTILINE
    )
    rx_platform = re.compile(
        r"^\s*System Description:\s+(?P<platform>.+)\n", re.MULTILINE)
    rx_platform1 = re.compile(r"^\s+1\s+(?P<platform>\S+)\s*\n", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s*Serial number : (?P<serial>\S+)")

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver1.search(v)
        r = {
            "vendor": "Iskratel",
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
                "HW version": match.group("hardware")
            }
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
