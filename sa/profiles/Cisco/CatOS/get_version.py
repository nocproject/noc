# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.CatOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
=======
##----------------------------------------------------------------------
## Cisco.CatOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_platform = re.compile(r"^Hardware\s+Version:\s+(?:\d|\.)+\s+Model:\s+(?P<platform>\S+)\s+Serial\s+#:\s+\S+$", re.MULTILINE | re.DOTALL)
rx_version = re.compile(r"^\S+\s+Software,\s+Version\s+\S+:\s+(?P<version>\S+)", re.MULTILINE | re.DOTALL)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Cisco.CatOS.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(noc.sa.script.Script):
    name = "Cisco.CatOS.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        v = self.cli("show version")
        platform = rx_platform.search(v).group("platform")
        version = rx_version.search(v).group("version")
        return {
            "vendor": "Cisco",
            "platform": platform,
            "version": version
        }
