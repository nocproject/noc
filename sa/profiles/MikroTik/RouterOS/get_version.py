# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
##
## MikroTik.RouterOS.get_version
##
class Script(NOCScript):
    name="MikroTik.RouterOS.get_version"
    cache=True
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"name=\"system\"\s+version=\"(?P<version>[^\"])\"", re.MULTILINE)
    def execute(self):
        v=self.cli("system package print detail")
        match=self.re_search(self.rx_ver, v)
        return {
            "vendor"    : "MikroTik",
            "platform"  : "RouterOS",
            "version"   : match.group("version"),
        }
    
