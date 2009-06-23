# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES4xxx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_sys=re.compile(r"BootRom Version\s+.*?(?P<platform>ES.+?)_",re.MULTILINE|re.DOTALL|re.IGNORECASE)
rx_ver=re.compile(r"SoftWare Package Version.*?_(?P<version>\d.+?)$",re.MULTILINE|re.DOTALL|re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES4xxx.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version 1")
        match_sys=rx_sys.search(v)
        match_ver=rx_ver.search(v)
        return {
            "vendor"    : "EdgeCore",
            "platform"  : match_sys.group("platform"),
            "version"   : match_ver.group("version"),
        }
