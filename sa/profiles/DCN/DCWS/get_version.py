# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DCN.DCWS.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"\s*(?P<platform>\S+)\s+Device.", re.MULTILINE)
    rx_ver = re.compile(r"^\s*Software\s+Version\s+(?P<version>\S+)\n", re.MULTILINE)
    rx_bver = re.compile(r"^\s*Bootrom\s+Version\s+(?P<bversion>\S+)\n", re.MULTILINE)
    rx_hver = re.compile(r"^\s*Hardware\s+Version\s+(?P<hversion>\S+)\n", re.MULTILINE)
    rx_serial = re.compile(r"^\s*Serial\s+No\s+(?P<serial>\S+)\n", re.MULTILINE)
    def execute(self):
        ver = self.cli("show version", cached=True)
        match = self.re_search(self.rx_platform, ver)
        vmatch = self.re_search(self.rx_ver, ver)
        bmatch = self.re_search(self.rx_bver, ver)
        hmatch = self.re_search(self.rx_hver, ver)
        smatch = self.re_search(self.rx_serial, ver)
        return {
            "vendor": "DCN",
            "platform": match.group("platform"),
            "version": vmatch.group("version"),
            "attributes": {
                "Bootrom version": bmatch.group("bversion"),
                "HW version": hmatch.group("hversion"),
                "Serial Number": smatch.group("serial")
                          }
            }
