# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(r"System description\s+:\s+(?P<platform>\S+).+System software version\s+:\s+v(?P<version>\S+), Release\(\d+\)", re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show version"))
        return {
            "vendor": "DLink",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
