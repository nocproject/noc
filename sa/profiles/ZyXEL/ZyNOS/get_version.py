# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx=re.compile(r"ZyNOS F/W Version\s+(?P<version>\S+).+Product Model\s+(?P<platform>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Zyxel.ZyNOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show system-information")
        match=rx.search(v.replace(":",""))
        return {
            "vendor"    : "Zyxel",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
