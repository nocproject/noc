# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Angtel.Topaz.get_version
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
    name = "Angtel.Topaz.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^\s*SW version\s+(?P<version>\S+).*\n"
        r"^\s*Boot version\s+(?P<bootprom>\S+).*\n"
        r"^\s*HW version\s*(?P<hardware>\S+)?.*\n", re.MULTILINE)
    rx_serial = re.compile(
        r"^\s*Serial number :\s*(?P<serial>\S+)?")

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "Angtel",
            "platform": "Topaz",
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom")
            }
        }
        if match.group("hardware"):
            r["attributes"]["HW version"] = match.group("hardware")
        v = self.cli("show system id", cached=True)
        match = self.re_search(self.rx_serial, v)
        if match.group("serial"):
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
