# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "SKS.SKS.get_version"
    interface = IGetVersion
    cache = True

    rx_ver = re.compile(
        r"^\s*SW version\s+(?P<version>\S+).*\n"
        r"^\s*Boot version\s+(?P<bootprom>\S+).*\n"
        r"^\s*HW version\s+(?P<hardware>\S+).*\n", re.MULTILINE)
    rx_platform = re.compile(
        r"^\s*System Description:\s+(?P<platform>.+)\n", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s*Serial number : (?P<serial>\S+)")

    rx_ver2 = re.compile(
        r"^(?P<platform>SKS\-\S+) Series Software, Version (?P<version>\S+)",
        re.MULTILINE
    )
    rx_rs = re.compile(
        r"^ROM: System Bootstrap, Version (?P<bootprom>\S+),\s*"
        r"hardware version:\s*(?P<hardware>\S+)\s*\n"
        r"^Serial num:\s*(?P<serial>\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        if match:
            r = {
                "vendor": "SKS",
                "version": match.group("version"),
                "attributes": {
                    "Boot PROM": match.group("bootprom"),
                    "HW version": match.group("hardware")
                }
            }
            v = self.cli("show system", cached=True)
            match = self.rx_platform.search(v)
            platform = match.group("platform")
            if platform == "SKS 10G":
                platform = "SKS-16E1-IP-1U"
            elif platform.startswith("SKS"):
                platform = "SW-24"
            r["platform"] = platform
            v = self.cli("show system id", cached=True)
            match = self.rx_serial.search(v)
            r["attributes"]["Serial Number"] = match.group("serial")
        else:
            match = self.rx_ver2.search(v)
            if match:
                r = {
                    "vendor": "SKS",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
                match = self.rx_rs.search(v)
                r["attributes"] = {
                    "Boot PROM": match.group("bootprom"),
                    "HW version": match.group("hardware"),
                    "Serial Number": match.group("serial")
                }
            else:
                t = parse_table(v)
                for i in t:
                    r = {
                        "vendor": "SKS",
                        "version": i[1],
                        "attributes": {
                            "Boot PROM": i[2],
                            "HW version": i[3]
                        }
                    }
                    break
                v = self.cli("show system", cached=True)
                t = parse_table(v)
                for i in t:
                    platform = i[1]
                    break
                if platform == "SKS 10G":
                    platform = "SKS-16E1-IP-1U"
                elif platform.startswith("SKS"):
                    platform = "SW-24"
                r["platform"] = platform
                v = self.cli("show system id", cached=True)
                t = parse_table(v)
                for i in t:
                    serial = i[1]
                    break
                r["attributes"]["Serial Number"] = serial

        return r
