# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.AireOS.get_version
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
## Cisco.AireOS.get_version
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

rx_ver = re.compile(r"^Product Version\.+\s+(?P<version>\S+)",
    re.MULTILINE | re.DOTALL)
rx_inv = re.compile("^PID:\s+(?P<platform>\S+)",
    re.MULTILINE | re.DOTALL)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Cisco.AireOS.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(noc.sa.script.Script):
    name = "Cisco.AireOS.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        v = self.cli("show sysinfo")
        match = rx_ver.search(v)
        version = match.group("version")
        v = self.cli("show inventory")
        match = rx_inv.search(v)
        platform = match.group("platform")
        return {
            "vendor": "Cisco",
            "platform": platform,
            "version": version,
        }
