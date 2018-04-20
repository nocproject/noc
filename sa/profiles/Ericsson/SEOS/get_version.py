# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Ericsson.SEOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ericsson.SEOS.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"^Active SBL\s+:\s+CXP:\s+(?P<version>\S+.*)\s+"
                        r"^Passive (?:NPU|SBL)\s+:\s+CXP:\s+[\S\s]+"
                        r"^Active BNS\s+:\s+CXCR:\s+(?P<sw_backup>\S+.*)$",
                        re.MULTILINE)

    def execute(self):
        ver = self.cli("show version", cached=True)
        for match in self.rx_ver.finditer(ver):
            version = match.group("version")
            sw_backup = match.group("sw_backup")
            return {
                "vendor": "Ericsson",
                "platform": "SEOS",
                "version": version,
                "attributes": {
                    "sw_backup": sw_backup
                }
            }
=======
##----------------------------------------------------------------------
## Ericsson.SEOS.get_version
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
    name = "Ericsson.SEOS.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(r"^[^-]*-(?P<version>[^-]+)-.*",
                        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor"   : "Ericsson",
            "platform" : "SEOS",
            "version"  : match.group("version"),
        }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
