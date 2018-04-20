# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.FWSM.get_version
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
## Cisco.FWSM.get_version
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

rx_ver = re.compile(r'FWSM Firewall Version (?P<version>\S+).*Hardware:\s+(?P<platform>\S+),', re.MULTILINE | re.DOTALL)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Cisco.FWSM.get_version"
    cache = True
    interface = IGetVersion
=======
class Script(noc.sa.script.Script):
    name = "Cisco.FWSM.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        self.cli("terminal pager 0")
        v = self.cli("show version")
        match = rx_ver.search(v)
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
