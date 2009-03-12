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

rx_ver=re.compile(r"Model:\s+(?P<platform>\S+).+JUNOS .*? \[(?P<version>[^\]]+)\]",re.MULTILINE|re.DOTALL)
rx_snmp_ver=re.compile(r"Juniper Networks, Inc.\s+(?P<platform>\S+).+?JUNOS\s+(?P<version>\S+)")

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v=self.snmp.get("1.3.6.1.2.1.1.1.0") # sysDescr.0
                match=rx_snmp_ver.search(v)
                return {
                    "vendor"    : "Juniper",
                    "platform"  : match.group("platform"),
                    "version"   : match.group("version"),
                }
            except self.snmp.TimeOutError:
                pass
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Juniper",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
