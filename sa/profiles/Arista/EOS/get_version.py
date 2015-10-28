# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Arista.EOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"Arista\s+(?P<platform>\S+).+"
        r"Software image version:\s+(?P<version>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Arista",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
