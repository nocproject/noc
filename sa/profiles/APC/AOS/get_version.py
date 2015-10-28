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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "APC.AOS.get_version"
    cache = True
    interface = IGetVersion

    rx_fwver = re.compile(r"Network Management Card AOS\s+v(?P<version>\S+)$",
                          re.MULTILINE)
    rx_platform = re.compile(r"^(?P<platform>.+?)\s+named\s+", re.MULTILINE)

    rx_platform1 = re.compile(r"^Name\s+: (?P<platform>.+?)\s+Date",
        re.MULTILINE)

    def execute(self):
        m = self.motd
        match = self.rx_platform.search(m)
        if not match:
            match = self.rx_platform1.search(m)
        platform = match.group("platform").strip()

        return {
            "vendor": "APC",
            "platform": platform,
            "version": self.re_search(self.rx_fwver, m).group("version")
            }
