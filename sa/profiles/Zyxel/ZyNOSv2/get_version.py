# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOSv2.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOSv2.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_ver = re.compile(r"^(?P<platform>.+?) version (?P<version>.+?)\s+",
    re.MULTILINE | re.DOTALL)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Zyxel.ZyNOSv2.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(noc.sa.script.Script):
    name = "Zyxel.ZyNOSv2.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        v = self.cli("version")
        match = rx_ver.search(v)
        return {
            "vendor": "Zyxel",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
