# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"^Force10 Networks .*Force10 Application Software Version: (?P<version>\S+).*(?:System|Chassis) Type: (?P<platform>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version | no-more")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Force10",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
