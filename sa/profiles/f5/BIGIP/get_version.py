# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx_ver = re.compile("BIG-IP Version (?P<version>.+?)$", re.MULTILINE)


class Script(BaseScript):
    name = "f5.BIGIP.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(
        r"Product\s+(?P<platform>\S+).+"
        r"Version\s+(?P<version>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show /sys version")
        match = self.rx_version.search(v)
        return {
            "vendor": "f5",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
