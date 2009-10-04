# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raritan.DominionSX.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"Firmware Version : (?P<version>\S+)",re.MULTILINE)

class Script(noc.sa.script.Script):
    name="Raritan.DominionSX.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Raritan",
            "platform"  : "SX",
            "version"   : match.group("version"),
        }
