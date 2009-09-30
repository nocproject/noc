# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Sun.iLOM3.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"SP firmware (?P<version>\S+)")

class Script(noc.sa.script.Script):
    name="Sun.iLOM3.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Sun",
            "platform"  : "iLOM3",
            "version"   : match.group("version"),
        }
