# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.iLO2.get_version
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
## HP.iLO2.get_version
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

rx_ver = re.compile(r"version=(?P<version>\S+)")


<<<<<<< HEAD
class Script(BaseScript):
    name = "HP.iLO2.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(noc.sa.script.Script):
    name = "HP.iLO2.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        v = self.cli("show /map1/firmware1/ version")
        match = rx_ver.search(v)
        return {
            "vendor": "HP",
            "platform": "iLO2",
            "version": match.group("version")
        }
