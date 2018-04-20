# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# f5.BIGIP.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
=======
##----------------------------------------------------------------------
## f5.BIGIP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

rx_ver = re.compile("BIG-IP Version (?P<version>.+?)$", re.MULTILINE)


<<<<<<< HEAD
class Script(BaseScript):
    name = "f5.BIGIP.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(NOCScript):
    name = "f5.BIGIP.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_version = re.compile(
        r"Product\s+(?P<platform>\S+).+"
        r"Version\s+(?P<version>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show /sys version")
        match = self.rx_version.search(v)
        return {
            "vendor": "f5",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
