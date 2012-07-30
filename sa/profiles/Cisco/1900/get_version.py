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
    name = "Cisco.1900.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(r"Version (?P<version>\S+).+cisco (?P<platform>Catalyst \d+? \S+? processor)", re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor"    : "Cisco",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
