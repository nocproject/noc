# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_platform=re.compile(r"Product Model\s+(?P<platform>\S+)",re.MULTILINE|re.DOTALL)
rx_version=re.compile(r"ZyNOS F/W Version\s+V?(?P<version>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Zyxel.ZyNOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show system-information")
        v=v.replace(":","")
        platform=rx_platform.search(v).group("platform")
        version=rx_version.search(v).group("version")
        return {
            "vendor"    : "Zyxel",
            "platform"  : platform,
            "version"   : version,
        }
