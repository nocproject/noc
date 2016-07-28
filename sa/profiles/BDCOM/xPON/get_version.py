# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BDCOM.xPON.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "BDCOM.xPON.get_version"
    cache = True
    interface = IGetVersion
    rx_ver = re.compile(
        r"BDCOM\(tm\)\s+(?P<platform>\S+)\s+\S+\s+Version\s+"
        r"(?P<version>\d+.\d+.\S+)\sBuild\s(?P<build>\d+).+"
        r"System Bootstrap,\sVersion\s(?P<boot>\d.\d.\d),\s"
        r"Serial num:(?P<serial>\d+)",
        re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(
        r"BDCOM\(tm\)\s+(?P<platform>\S+)\s+\S+\s+Version\s+"
        r"(?P<version>\d+.\d+.\S+)\sBuild\s(?P<build>\d+).+"
        r"System Bootstrap,Version\s(?P<boot>\d.\d.\d),"
        r"Serial num:(?P<serial>\d+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.has_snmp():
            try:
                # sysDescr.0
                v = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                if v:
                    match = self.re_search(self.rx_snmp_ver, v)
                    return {
                        "vendor": "BDCOM",
                        "platform": match.group("platform"),
                        "version": match.group("version"),
                        "attributes": {
                            "build": match.group("build"),
                            "boot": match.group("boot"),
                            "serial": match.group("serial")
                        }
                    }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        if match:
            return {
                "vendor": "BDCOM",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {
                    "build": match.group("build"),
                    "boot": match.group("boot"),
                    "serial": match.group("serial")
                }

            }
        return r
