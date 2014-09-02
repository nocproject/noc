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

    rx_ver = re.compile(
        r"^(?:Cisco IOS Software,.*?|IOS \(tm\)) (IOS-XE Software,\s)?"
        r"(?P<platform>.+?) Software \((?P<image>[^)]+)\), (Experimental )?"
        r"Version (?P<version>[^\s,]+)", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(
        r"^(?:Cisco IOS Software,.*?|IOS \(tm\)) (?P<platform>.+?) Software "
        r"\((?P<image>[^)]+)\), (Experimental )?Version (?P<version>[^,]+),",
        re.MULTILINE | re.DOTALL)
    rx_platform = re.compile(
        r"^cisco (?P<platform>\S+) \(\S+\) processor( \(revision \S+\))? with",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                if v:
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
        platform = match.group("platform")
        if platform in ["IOS-XE", "EGR"]:
            # Process IOS XE platform
            pmatch = self.re_search(self.rx_platform, v)
            if pmatch:
                platform = pmatch.group("platform")
        return {
            "vendor": "Cisco",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {
                "image": match.group("image"),
            }
        }
