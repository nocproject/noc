# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Dell.Powerconnect.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(
        r"Machine Model\.+ (?P<platform>\S+).+?"
        r"Software Version\.+ (?P<version>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        s = self.cli("show tech-support", cached=True)
        match = self.re_search(self.rx_ver, s)
        return {
            "vendor": "Dell",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
