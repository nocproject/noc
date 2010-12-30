# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_version
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
##
## HP.ProCurve9xxx.get_version
##
class Script(NOCScript):
    name="HP.ProCurve9xxx.get_version"
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"^Image stamp:\s+\S+\n[^\n]+?\n\s*(?P<version>\S+)\n\s+\S+\nBoot Image:\s+\S+\n$",re.MULTILINE|re.DOTALL)
    rx_snmp_ver=re.compile(r"ProCurve\s+\S+\s+\S+\s(?P<platform>\S+)\,\s+\S+\s+Version\s+(?P<version>\S+).+$")
    rx_motd=re.compile(r"ProCurve\s+\S+\s+(?P<platform>\S+)",re.IGNORECASE|re.MULTILINE)
    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v=self.snmp.get("1.3.6.1.2.1.1.1.0") # sysDescr.0
                match=self.re_search(self.rx_snmp_ver, v)
                return {
                    "vendor"    : "HP",
                    "platform"  : match.group("platform"),
                    "version"   : match.group("version"),
                }
            except self.snmp.TimeOutError:
                pass
        # ProCurve does not returns platform via CLI,
        # While still displays it in message of the day
        # Try to fetch platform
        match=self.re_search(self.rx_motd, self.motd)
        platform=match.group("platform") if match else "ProCurve"
        # Get version
        v=self.cli("show version")
        match=self.re_search(self.rx_ver, v)
        return {
            "vendor"    : "HP",
            "platform"  : platform,
            "version"   : match.group("version"),
        }
    
