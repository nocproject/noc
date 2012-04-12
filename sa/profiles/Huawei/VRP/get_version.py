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

rx_ver = re.compile(r"^VRP.+Software, Version (?P<version>[^ ,]+),? .*?Quidway (?P<platform>(?:NetEngine\s+)?\S+)[^\n]+uptime", re.MULTILINE | re.DOTALL | re.IGNORECASE)
rx_ver_snmp = re.compile(r"Versatile Routing Platform Software.*?Version (?P<version>[^ ,]+),? .*?Quidway (?P<platform>(?:NetEngine\s+)?[^ \t\n\r\f\v\-]+)[^\n]+", re.MULTILINE | re.DOTALL | re.IGNORECASE)
rx_ver_snmp2 = re.compile(r"(?P<platform>(?:\S+\s+)?S\d+(?:[A-Z]+-[A-Z]+)?(?:\d+\S+)?)\s+Huawei\sVersatile\sRouting\sPlatform\sSoftware.*Version\s(?P<version>\d+\.\d+)\s\(S\d+\s(?P<image>\S+)+\).*", re.MULTILINE | re.DOTALL | re.IGNORECASE)

class Script(noc.sa.script.Script):
    name = "Huawei.VRP.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        v = ""
        if self.snmp and self.access_profile.snmp_ro:
            # Trying SNMP
            try:
                # SNMPv2-MIB::sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
            except self.snmp.TimeOutError:
                pass
        if v == "":
            # Trying CLI
            try:
                v = self.cli("display version", cached=True)
            except self.CLISyntaxError:
                raise self.NotSupportedError()
        rx = self.find_re([rx_ver, rx_ver_snmp, rx_ver_snmp2], v)
        for match in rx.finditer(v):
            platform = match.group("platform")
            # Convert NetEngine to NE
            if platform.lower().startswith("netengine "):
                n, p = platform.split(" ", 1)
                platform = "NE%s" % p.strip().upper()
            r = {
                "vendor": "Huawei",
                "platform": platform,
                "version": match.group("version")
            }
            if self.snmp and self.access_profile.snmp_ro:
                img = rx_ver_snmp2.search(v)
                if img:
                    r.update({"attributes": { }})
                    r["attributes"].update({"image": img.group("image")})
            return r
