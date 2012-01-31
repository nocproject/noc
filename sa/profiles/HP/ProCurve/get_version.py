# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "HP.ProCurve.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(r"ProCurve\s+\S+\s+(Switch\s+)?(?P<platform>\S+).*?,\s*revision\s+(?P<version>\S+),", re.IGNORECASE)

    def execute(self):
        v = None
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
            except self.snmp.TimeOutError:
                pass  # Fallback to CLI
        if not v:
            v = self.cli("walkMIB sysDescr")
        match = self.re_search(self.rx_ver, v.strip())
        return {
            "vendor": "HP",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
