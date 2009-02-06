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

rx=re.compile(r"Product Name:\s+(?P<platform>\S+)$.+Software Version:\s+(?P<version>.+?)\s*\,",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Juniper.ScreenOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("get system")
        match=rx.search(v)
        return {
            "vendor"    : "Juniper",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
