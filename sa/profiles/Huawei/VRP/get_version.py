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

rx_ver=re.compile(r"^VRP.+Software, Version (?P<version>[^ ,]+),? .*?Quidway (?P<platform>(?:NetEngine\s+)?\S+)[^\n]+uptime",re.MULTILINE|re.DOTALL|re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="Huawei.VRP.get_version"
    cache=True
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("display version")
        match=rx_ver.search(v)
        platform=match.group("platform")
        # Convert NetEngine to NE
        if platform.lower().startswith("netengine "):
            n,p=platform.split(" ",1)
            platform="NE%s"%p.strip().upper()
        return {
            "vendor"    : "Huawei",
            "platform"  : platform,
            "version"   : match.group("version"),
        }
