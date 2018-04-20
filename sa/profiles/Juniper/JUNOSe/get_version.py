# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx_ver = re.compile(
    r"Juniper\s+(Edge Routing Switch )?(?P<platform>.+?)$.+"
    r"Version\s+(?P<version>.+?)\s*\[BuildId (?P<build>\d+)",
    re.MULTILINE | re.DOTALL)
rx_snmp_ver = re.compile(
    r"Juniper Networks, Inc.\s+(?P<platform>\S+).+?SW Version\s:"
    r"\s\((?P<version>[A-Za-z0-9\- \.\[\]]+)\)")

class Script(BaseScript):
    name = "Juniper.JUNOSe.get_version"
    cache = True
    interface = IGetVersion


    def execute(self):
        if self.has_snmp():
            try:
                v = self.snmp.get("1.3.6.1.2.1.1.1.0")  # sysDescr.0
                match = rx_snmp_ver.search(v)
                if match is None:
                    raise self.snmp.TimeOutError()
                return {
                    "vendor": "Juniper",
                    "platform": match.group("platform"),
                    "version": match.group("version"),
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version")
        match = self.re_search(rx_ver, v.replace(":", ""))
=======
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
##
## Juniper.JUNOSe.get_version
##
class Script(NOCScript):
    name="Juniper.JUNOSe.get_version"
    cache=True
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"Juniper\s+(Edge Routing Switch )?(?P<platform>.+?)$.+Version\s+(?P<version>.+?)\s*\[",re.MULTILINE|re.DOTALL)
    def execute(self):
        v=self.cli("show version")
        match=self.re_search(self.rx_ver, v.replace(":", ""))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return {
            "vendor": "Juniper",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Build": match.group("build"),
            }
        }
    
