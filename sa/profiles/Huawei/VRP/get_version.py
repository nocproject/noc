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

rx_ver=re.compile(r"^VRP Software, Version (?P<version>\S+), .*?Quidway (?P<platform>\S+) uptime",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Huawei.VRP.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("display version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Huawei",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
