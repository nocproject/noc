# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
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
    name = "Cisco.IOS.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(r"^(?:Cisco IOS Software,.*?|IOS \(tm\)) (?P<platform>.+?) Software \((?P<image>[^)]+)\), Version (?P<version>[^,]+),", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(r"^(?:Cisco IOS Software,.*?|IOS \(tm\)) (?P<platform>.+?) Software \((?P<image>[^)]+)\), Version (?P<version>[^,]+),", re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.re_search(self.rx_snmp_ver, v)
                return {
                    "vendor": "Cisco",
                    "platform": match.group("platform"),
                    "version": match.group("version"),
                    "attributes": {
                        "image": match.group("image"),
                    }
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "image": match.group("image"),
            }
        }
