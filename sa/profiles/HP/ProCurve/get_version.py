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

rx_ver=re.compile(r"^Image stamp:\s+\S+\n[^\n]+?\n\s*(?P<version>\S+)\n\s+\S+\nBoot Image:\s+\S+\n$",re.MULTILINE|re.DOTALL)
rx_snmp_ver=re.compile(r"^ProCurve\s+\S+\s+(?P<platform>\S+).*?,\s+revision\s+(?P<version>\S+),.+$")
rx_motd=re.compile(r"ProCurve\s+\S+\s+(?P<platform>\S+)",re.IGNORECASE|re.MULTILINE)

class Script(noc.sa.script.Script):
    name="HP.ProCurve.get_version"
    implements=[IGetVersion]
    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v=self.snmp.get("1.3.6.1.2.1.1.1.0") # sysDescr.0
                match=rx_snmp_ver.search(v)
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
        match=rx_motd.search(self.motd)
        platform=match.group("platform") if match else "ProCurve"
        # Get version
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "HP",
            "platform"  : platform,
            "version"   : match.group("version"),
        }
