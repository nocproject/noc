# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"\n\n(?P<platform>\S+) .+Software Version (?P<version>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="HP.GbE2.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("/info/sys/general")
        self.cli("/")
        match=rx_ver.search(v)
        return {
            "vendor"    : "HP",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
