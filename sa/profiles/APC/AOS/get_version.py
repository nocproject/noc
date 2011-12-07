# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## APC.AOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "APC.AOS.get_version"
    cache = True
    implements = [IGetVersion]

    rx_fwver = re.compile(r"Network Management Card AOS\s+v(?P<version>\S+)$",
                          re.MULTILINE)
    rx_platform = re.compile(r"^(?P<platform>.+)named.*$",
                             re.MULTILINE)

    def execute(self):
        m = self.motd
        r = {
            "vendor": "APC",
            }
        match = self.rx_fwver.search(m)
        if match:
            r["version"] = match.group("version")
        match = self.rx_platform.search(m)
        if match:
            r["platform"] = match.group("platform").strip()
        return r
