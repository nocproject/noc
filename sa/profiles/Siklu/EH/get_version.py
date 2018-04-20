# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Siklu.EH.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
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
    name = "Siklu.EH.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Siklu.EH.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
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
    name = "Siklu.EH.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_sys = re.compile(r"^system description\s+: (?P<platform>.+?)$",
        re.MULTILINE)
    rx_ver = re.compile(
        r"^\d+\s+(?P<version>\S+)\s+\S+\s+\S+\s+yes\s+\S+\s+\S+",
        re.MULTILINE)

    def execute(self):
<<<<<<< HEAD
        v = self.cli("show sw")
=======
        v =self.cli("show sw")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        match_ver = self.re_search(self.rx_ver, v)

        v = self.cli("show system description")
        match_sys = self.re_search(self.rx_sys, v)
        return {
            "vendor": "Siklu",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
