# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES3xxx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"Device Type\s+:\s+(?P<platform>\S+).+Firmware Version\s+:\s+(?:Build\s+)?(?P<version>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="DLink.DES3xxx.get_version"
    implements=[IGetVersion]
    def execute(self):
        self.cli("disable clipaging")
        data=self.cli("show switch")
        match=rx_ver.search(data)
        return {
            "vendor"    : "DLink",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
