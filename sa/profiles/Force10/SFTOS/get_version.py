# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.SFTOS.get_version
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
    name = "Force10.SFTOS.get_version"
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Catalog Number\.+\s+(?P<platform>\S+).+?"
        r"^Software Version\.+\s+(?P<version>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Force10",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
