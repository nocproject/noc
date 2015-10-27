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



class Script(noc.sa.script.Script):
    name = "Cisco.NXOS.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(r"^Cisco Nexus Operating System \(NX-OS\) Software.+?Software.+?system:\s+version\s+(?P<version>\S+).+?Hardware\s+cisco\s+\S+\s+(?P<platform>\S+)", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(r"^Cisco NX-OS\(tm\) .*?Version (?P<version>[^,]+),", re.IGNORECASE)
    rx_snmp_platform = re.compile(r"^Nexus\d+ (?P<platform>C\d+) .+Chassis$")

    def execute(self):
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
                match = self.rx_snmp_ver.search(v)
                version = match.group("version")
                # Get platform via ENTITY-MIB
                platform = None
                # ENTITY-MIB::entPhysicalName
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.47.1.1.1.1.7"):
                    match = self.rx_snmp_platform.match(v)
                    if match:
                        platform = match.group("platform")
                        break
                #
                return {
                    "vendor": "Cisco",
                    "platform": platform,
                    "version": version,
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version | no-more")
        match = self.rx_ver.search(v)
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
