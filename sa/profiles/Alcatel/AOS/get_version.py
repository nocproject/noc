# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_sys=re.compile(r"Module in slot.+?Model.*?Name:\s+(?P<platform>.+?),$",re.MULTILINE|re.DOTALL)
rx_ver=re.compile(r"System.*?Description:\s+(?P<version>.+?)\s.*$",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Alcatel.AOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show ni")
        match_sys=rx_sys.search(v)
        v=self.cli("show system")
        match_ver=rx_ver.search(v)
        return {
            "vendor"    : "Alcatel",
            "platform"  : match_sys.group("platform"),
            "version"   : match_ver.group("version"),
        }
