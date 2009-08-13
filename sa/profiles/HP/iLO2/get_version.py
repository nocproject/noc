# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.iLO2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"version=(?P<version>\S+)")

class Script(noc.sa.script.Script):
    name="HP.iLO2.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show /map1/firmware1/ version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "HP",
            "platform"  : "iLO2",
            "version"   : match.group("version"),
        }
