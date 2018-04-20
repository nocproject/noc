# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS_EE.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Zyxel.ZyNOS_EE.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_ver = re.compile(
        r"^\sZyNOS version\s:\s+V?(?P<version>\S+).+^\sbootbase version\s:\s+V?(?P<bootprom>\S+).+^\sProduct Model\s:\s+(?P<platform>\S+).",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        ver = self.cli("sys mrd atsh")
        match = self.re_search(self.rx_ver, ver)
        r = {
            "vendor": "Zyxel",
            "platform": match.group("platform") + 'EE',
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
            }
        }
        return r
