# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Dell.Powerconnect62xx.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Dell.Powerconnect62xx.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Dell.Powerconnect62xx.get_version
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
    name = "Dell.Powerconnect62xx.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_ver = re.compile(
        r"Machine Model\.+ (?P<platform>\S+).+?"
        r"Serial Number\.+ (?P<serial>\S+).+?"
        r"Software Version\.+ (?P<version>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        s = self.cli("show tech-support", cached=True)
        match = self.re_search(self.rx_ver, s)
        return {
            "vendor": "Dell",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Serial Number": match.group("serial")
            }
        }
