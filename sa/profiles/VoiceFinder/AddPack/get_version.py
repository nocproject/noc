# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VoiceFinder.AddPack.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"(?P<platform>\S+) System software Revision (?P<version>\S+)",re.MULTILINE|re.DOTALL|re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="VoiceFinder.AddPack.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "AddPack",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
