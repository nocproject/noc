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

rx_ver=re.compile(r"^(?:Cisco IOS Software,.*?|IOS \(tm\)) (?P<platform>.+?) Software \((?P<image>[^)]+)\), Version (?P<version>[^,]+),",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        self.cli("terminal length 0")
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Cisco",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
            "image"     : match.group("image"),
        }
