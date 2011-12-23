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
    rx_platform = re.compile(r"^(?P<platform>.+?)\s+named\s+", re.MULTILINE)

    def execute(self):
        m = self.motd
        return {
            "vendor": "APC",
            "platform": self.re_search(self.rx_platform, m).group("platform"),
            "version": self.re_search(self.rx_fwver, m).group("version")
            }
