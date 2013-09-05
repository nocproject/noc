# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Cisco.IOSXR.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(
        r"^Cisco IOS XR Software, Version\s+(?P<version>\S+)\[\S+\].+"
        r"cisco\s+(?P<platform>\S+)(?: Series)? \([^)]+\) processor with \d+",
        re.MULTILINE | re.DOTALL
    )
    rx_snmp_ver = re.compile(r"Cisco IOS XR Software \(Cisco (?P<platform>\S+)\s+\w+\).+\s+Version\s+(?P<version>\S+)\[\S+\]")

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)  # sysDescr.0
                match = self.re_search(self.rx_snmp_ver, v)
                return {
                    "vendor": "Cisco",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
