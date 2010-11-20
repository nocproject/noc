# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"^Version:\s+(?P<version>\S+)",re.MULTILINE)

class Script(noc.sa.script.Script):
    name="Vyatta.Vyatta.get_version"
    cache=True
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Vyatta",
            "platform"  : "VC",
            "version"   : match.group("version"),
        }
