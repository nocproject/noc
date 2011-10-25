# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.OS62xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Alcatel.OS62xx.get_version"
    cache = True
    implements = [IGetVersion]

    rx_sys = re.compile(r"System Description:\s+(?P<platform>.+?)$",
                        re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(r"SW version\s+(?P<version>\S+)",
                        re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.7.68420352",
                                         cached=True)  # Platform
                hwver = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67108992",
                                      cached=True)  # HW Version
                fwver = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992",
                                      cached=True)  # FW version
                bprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67108992",
                                      cached=True)  # Boot PROM
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67108992",
                                       cached=True)  # Serial number
                return {
                    "vendor": "Alcatel",
                    "platform": platform,
                    "version": fwver,
                    "attributes": {
                        "Boot PROM": bprom,
                        "HW version": hwver,
                        "Serial Number": serial
                    }
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show system")
        match_sys = self.re_search(self.rx_sys, v)
        v = self.cli("show version")
        match_ver = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version"),
        }
