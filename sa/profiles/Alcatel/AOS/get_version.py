# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.AOS.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"Module in slot.+?Model.*?Name:\s+(?P<platform>.+?),$",
        re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(r"System.*?Description:\s+(?P<version>.+?)\s.*$",
        re.MULTILINE | re.DOTALL)
    rx_ver1 = re.compile(
        r"System.*?Description:\s+Alcatel-Lucent\s+\S+\s+(?P<version>\S+)\s.*$",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show ni")
        match_sys = self.rx_sys.search(v)
        v = self.cli("show system")
        match_ver = self.rx_ver.search(v)
        if match_ver.group("version") == "Alcatel-Lucent":
            match_ver = self.rx_ver1.search(v)
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
