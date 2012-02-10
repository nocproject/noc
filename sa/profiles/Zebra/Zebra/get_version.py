# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zebra.Zebra.get_version
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
    name = "Zebra.Zebra.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(r"^(?P<platfrom>\S+)\s+(?P<version>\S+)\s+.*$",
                        re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        return {
            "vendor": "Zebra",
            "platform": match.group("platfrom"),
            "version": match.group("version"),
        }
