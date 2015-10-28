# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.FWSM.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_ver = re.compile(r'FWSM Firewall Version (?P<version>\S+).*Hardware:\s+(?P<platform>\S+),', re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Cisco.FWSM.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        self.cli("terminal pager 0")
        v = self.cli("show version")
        match = rx_ver.search(v)
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
