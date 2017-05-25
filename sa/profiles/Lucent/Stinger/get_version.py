# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
#  Lucent.Stinger.get_version
# ---------------------------------------------------------------------
#  Copyright (C) 2007-2017 The NOC Project
#  See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Lucent.Stinger.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(r"Software version\s*(?P<version>\S+)\n(\n|)"
                        r"Hardware revision:\s(?P<revision>\S+)\s+(?P<platform>\S+)\s(?P<description>.+)",
                        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        r = {}
        v = self.cli("version")
        match = self.rx_ver.match(v)

        if match:
            r = {
                "vendor": "Lucent",
                "platform": match.group("platform"),
                "version": match.group("version"),
                "attributes": {
                    "HW version": match.group("revision")
                }
            }

        return r
