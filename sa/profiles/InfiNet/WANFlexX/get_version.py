# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_version"
    cache = True
    interface = IGetVersion
    
    rx_ver = re.compile(r"^(?P<platform>.+?)\s+WANFleX\s+(?P<version>\S+)",
                        re.MULTILINE)

    def execute(self):
        cmd = self.cli("system version")
        match = self.rx_ver.search(cmd.strip())
=======
##----------------------------------------------------------------------
## InfiNet.WANFlexX.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver = re.compile(r"^(?P<platform>.+?)\s+WANFleX\s+(?P<version>\S+)",
    re.MULTILINE | re.DOTALL)


class Script(noc.sa.script.Script):
    name = "InfiNet.WANFlexX.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        v = self.cli("system version")
        match = rx_ver.search(v.strip())
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return {
            "vendor": "InfiNet",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
