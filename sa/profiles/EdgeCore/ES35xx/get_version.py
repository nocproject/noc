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

rx_sys=re.compile(r"System description:\s+.*?(?P<platform>ES.+?)$",re.MULTILINE|re.DOTALL|re.IGNORECASE)
rx_ver=re.compile(r"Operation code version\s+(?P<version>\S+)",re.MULTILINE|re.DOTALL|re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES35xx.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show system")
        match_sys=rx_sys.search(v)
        v=self.cli("show version")
        match_ver=rx_ver.search(v.replace(":",""))
        return {
            "vendor"    : "EdgeCore",
            "platform"  : match_sys.group("platform"),
            "version"   : match_ver.group("version"),
        }
