# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_version
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

rx_ver = re.compile(r"^.*?Switch\s(?P<platform>.+?)\sSoftware\s\Version\s3Com\sOS\sV(?P<version>.+?)$", re.MULTILINE | re.DOTALL | re.IGNORECASE)


class Script(NOCScript):
    name = "H3C.VRP.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        v = self.cli("display version")
        match = rx_ver.search(v)
        platform = match.group("platform")
        return {
            "vendor": "H3C",
            "platform": platform,
            "version": match.group("version")
        }
