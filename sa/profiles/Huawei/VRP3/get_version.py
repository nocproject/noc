# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_version
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Huawei.VRP3.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(r"\S+\s+(?P<version>\S+)\((?P<platform>\S+)\) Version , RELEASE SOFTWARE")
    rx_bios = re.compile(r"\s+BIOS Version is\s+(?P<bios>\S+)")

    def execute(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v)
        r = {
            "vendor": "Huawei",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
        bios = self.rx_bios.search(v)
        if bios:
            r.update({"attributes": {}})
            r["attributes"].update({"Boot PROM": bios.group("bios")})
        return r
