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

rx_ver=re.compile(r"^Cisco Nexus Operating System \(NX-OS\) Software.+?Software.+?system:\s+version\s+(?P<version>\S+).+?Hardware\s+cisco\s+\S+\s+(?P<platform>\S+)",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Cisco.NXOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version | no-more")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Cisco",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
