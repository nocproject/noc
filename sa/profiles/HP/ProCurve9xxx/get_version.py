# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "HP.ProCurve9xxx.get_version"
    cache = True
    interface = IGetVersion

    rx_sw_ver = re.compile(r"SW:\sVersion\s(?P<version>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_hw_ver = re.compile(r"HW:\sProCurve\s(?P<version>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(r"ProCurve\s+\S+\s+\S+\s(?P<platform>\S+)\,\s+\S+\s+Version\s+(?P<version>\S+).+$")

    def execute(self):
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
                match = self.re_search(self.rx_snmp_ver, v)
                return {
                    "vendor": "HP",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
            except self.snmp.TimeOutError:
                pass

        # Get version
        v = self.cli("show version", cached=True)
        match1 = self.re_search(self.rx_sw_ver, v)
        match2 = self.re_search(self.rx_hw_ver, v)
        return {
            "vendor": "HP",
            "platform": match2.group("version"),
            "version": match1.group("version")
        }
