# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.ALS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alstec.ALS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^\s*SW version\s+(?P<version>\S+).*\n"
        r"^\s*Boot version\s+(?P<bootprom>\S+).*\n"
        r"(^\s*HW version\s+(?P<hardware>\S+).*\n)?", re.MULTILINE)
    rx_platform = re.compile(
        r"^\s*System Description:\s+(?P<platform>.+)\n", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s*Serial number : (?P<serial>\S+)")

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "Alstec",
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom")
            }
        }
        if match.group("hardware"):
            r["attributes"]["HW version"] = match.group("hardware")
        v = self.cli("show system", cached=True)
        match = self.re_search(self.rx_platform, v)
        platform = match.group("platform")
        if platform == "24-port 10/100 Ethernet Switch":
            platform = "ALS-62000 L2"
        r["platform"] = platform
        v = self.cli("show system id", cached=True)
        match = self.rx_serial.search(v)
        if match:
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
