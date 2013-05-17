# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(
        r"version: (?P<version>\d+\.\d+).+board-name: (?P<platform>\D+.\S+)",
        re.MULTILINE | re.DOTALL)
    rx_rb = re.compile(
        r"serial-number: (?P<serial>\S+).+current-firmware: "
        r"(?P<boot>\d+\.\d+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("system resource print")
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "MikroTik",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
        if r["platform"] != "x86":
            v = self.cli("system routerboard print")
            v = self.cli("system routerboard print")
            rb = self.re_search(self.rx_rb, v)
            if rb:
                r.update({"attributes": {}})
                r["attributes"].update({"Serial Number": rb.group("serial")})
                r["attributes"].update({"Boot PROM": rb.group("boot")})
        return r
