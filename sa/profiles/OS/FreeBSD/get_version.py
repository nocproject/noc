# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unix.FreeBSD.get_version
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
## OS.FreeBSD.get_version
##
class Script(NOCScript):
    name="OS.FreeBSD.get_version"
    cache=True
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"(?P<version>\S+)\s+(?P<platform>\S+)",re.MULTILINE|re.DOTALL)
    def execute(self):
        data=self.cli("/usr/bin/uname -m -r")
        match=self.re_search(self.rx_ver, data)
        return {
            "vendor"    : "FreeBSD",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
    
