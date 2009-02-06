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

rx_ver=re.compile(r"ProductCode (?P<version>\S+) build.*Hardware type: (?P<platform>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Protei.MediaGateway.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("_version full")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Protei",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
