# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InfiNet.WANFlexX.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"^(?P<platform>.+?)\s+WANFleX\s+(?P<version>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="InfiNet.WANFlexX.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("system version")
        match=rx_ver.search(v.strip())
        return {
            "vendor"    : "InfiNet",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
