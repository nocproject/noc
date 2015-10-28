# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re
from noc.sa.profiles.DLink.DxS_Smart import (DES1210, DGS121048, DGS121052)


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"system hardware version\s+:\s+(?P<hardware>\S+).+"
        r"system firmware version\s+:\s+(?P<version>\S+).+system boot"
        r" version\s+:\s+(?P<bootprom>\S+).+system protocol version\s+:"
        r"\s+(?P<protover>\S+).+system serial number\s+:\s+(?P<serial>\S+)",
        re.MULTILINE | re.DOTALL | re.I
    )
    rx_snmp_ver = re.compile(r"^(?P<platform>\S+)\s*", re.DOTALL)

    def execute(self):
        r = {"vendor": "DLink"}
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.re_search(self.rx_snmp_ver, v)
                r.update({"platform": match.group("platform")})
            except self.snmp.TimeOutError:
                pass
        else:
            raise self.NotSupportedError()
        if DES1210(r) or DGS121048(r) or DGS121052(r):
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
