# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_version
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
## Vyatta.Vyatta.get_version
##
class Script(NOCScript):
    name="Vyatta.Vyatta.get_version"
    cache=True
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"^Version:\s+(?P<version>\S+)",re.MULTILINE)
    def execute(self):
        v=self.cli("show version")
        match=self.re_search(self.rx_ver, v)
        return {
            "vendor"    : "Vyatta",
            "platform"  : "VC",
            "version"   : match.group("version"),
        }
    
