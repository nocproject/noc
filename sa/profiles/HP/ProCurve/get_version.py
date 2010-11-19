# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"ProCurve\s+\S+\s+(Switch\s+)?(?P<platform>\S+).*?,\s*revision\s+(?P<version>\S+),",re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="HP.ProCurve.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=None
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v=self.snmp.get("1.3.6.1.2.1.1.1.0") # sysDescr.0
            except self.snmp.TimeOutError:
                pass
        if not v:
            v=self.cli("walkMIB sysDescr")
        match=rx_ver.search(v.strip())
        return {
            "vendor"    : "HP",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
