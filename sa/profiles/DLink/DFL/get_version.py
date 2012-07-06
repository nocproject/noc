# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DFL.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
import re


class Script(NOCScript):
    name = "DLink.DFL.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        rx_ver = re.compile(r"^D-Link Firewall (?P<version>\S+)",
            re.MULTILINE | re.DOTALL | re.IGNORECASE)
        rx_dev = re.compile(r"^\s+Name:\s+(?P<platform>\S+)",
            re.MULTILINE | re.DOTALL | re.IGNORECASE)

        v = self.cli("about", cached=True)
        match = rx_ver.search(v)
        version = match.group("version")
        v = self.cli("show Device", cached=True)
        match = rx_dev.search(v)
        platform = match.group("platform")

        return {
            "vendor": "DLink",
            "platform": platform,
            "version": version
        }
