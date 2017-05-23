# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ericsson.SEOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
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
