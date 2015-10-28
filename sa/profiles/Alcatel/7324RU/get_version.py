# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7324RU.get_config
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re

rx_sys = re.compile(r"Model\s*:\s*(?P<platform>.+?)\s*$",
    re.MULTILINE | re.DOTALL)
rx_ver = re.compile(r".+?version\s*:\s*(?P<version>.+?)\s+\|.*$",
    re.MULTILINE | re.DOTALL)

class Script(BaseScript):
    name = "Alcatel.7324RU.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        v = self.cli("sys info show")
        match_sys = rx_sys.search(v)
        match_ver = rx_ver.search(v)
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
