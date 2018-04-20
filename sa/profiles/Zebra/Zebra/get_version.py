# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zebra.Zebra.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Zebra.Zebra.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Zebra.Zebra.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Zebra.Zebra.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_ver = re.compile(r"^(?P<platfrom>\S+)\s+(?P<version>\S+)\s+.*$",
                        re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        return {
            "vendor": "Zebra",
            "platform": match.group("platfrom"),
            "version": match.group("version"),
        }
