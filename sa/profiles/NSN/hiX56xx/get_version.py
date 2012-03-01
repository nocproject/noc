# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NSN.hiX56xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re


class Script(noc.sa.script.Script):
    name = "NSN.hiX56xx.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(
        r"System version\s+:\s+(?P<platform>\S+)/(?P<version>\S+)")

    def execute(self):
        s = self.cli("show system-version", cached=True)
        match = self.re_search(self.rx_ver, s)
        r = {
            "vendor": "NSN",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
        return r
