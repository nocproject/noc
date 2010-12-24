# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
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
## Juniper.JUNOSe.get_version
##
class Script(NOCScript):
    name="Juniper.JUNOSe.get_version"
    cache=True
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"Juniper\s+(Edge Routing Switch )?(?P<platform>.+?)$.+Version\s+(?P<version>.+?)\s*\[",re.MULTILINE|re.DOTALL)
    def execute(self):
        v=self.cli("show version")
        match=self.re_search(self.rx_ver, v.replace(":", ""))
        return {
            "vendor"    : "Juniper",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
    
