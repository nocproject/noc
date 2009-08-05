# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOSv2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"^(?P<platform>.+?) version (?P<version>.+?)\s+",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Zyxel.ZyNOSv2.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Zyxel",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
