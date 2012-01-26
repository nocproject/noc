# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re
from noc.sa.profiles.DLink.DxS_Smart import DES1210


class Script(noc.sa.script.Script):
    name = "DLink.DxS_Smart.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(r"System hardware version\s+:\s+(?P<hardware>\S+).+System firmware version\s+:\s+(?P<version>\S+).+System boot version\s+:\s+(?P<bootprom>\S+).+System serial number\s+:\s+(?P<serial>\S+)", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(r"Serial Number\s+:\s+(?P<serial>\S+)", re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(r"^(?P<platform>\S+)\s*", re.DOTALL)

    def execute(self):
        r = {"vendor": "DLink"}
        if self.snmp and self.access_profile.snmp_ro:
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)  # sysDescr.0
                print v
                match = self.re_search(self.rx_snmp_ver, v)
                r.update({"platform": match.group("platform")})
            except self.snmp.TimeOutError:
                pass
        else:
            raise self.NotSupportedError()
        if DES1210(r):
            s = self.cli("show switch", cached=True)
            match = self.re_search(self.rx_ver, s)
            r.update({
                "version": match.group("version"),
                "attributes": {
                    "Boot PROM": match.group("bootprom"),
                    "HW version": match.group("hardware"),
                    "Serial Number": match.group("serial")
                }
            })
            return r
        else:
            raise self.NotSupportedError()
