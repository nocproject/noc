# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Polygon.IOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2019 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Polygon.IOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Attika (?P<platform>\S+)\n.+,\s(?:Version:)?\s(?P<version>\S+\s\S+).+\n.+\n.+\n(?:System image file is)"
        r"?\s(?P<image><.+>)", re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        platform = match.group("platform")
        s = self.snmp.get(mib["1.3.6.1.4.1.14885.1001.6004.1.3.1.11.0.0.1"])
        r = {
            "vendor": "Polygon",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {
                "image": match.group("image"),
            }
        }
        if s:
            r["attributes"]["Serial Number"] = s
        return r
