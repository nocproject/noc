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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion

rx_ver = re.compile("BIG-IP Version (?P<version>.+?)$", re.MULTILINE)


class Script(NOCScript):
    name = "f5.BIGIP.get_version"
    cache = True
    implements = [IGetVersion]

    rx_version = re.compile(
        r"Product\s+(?P<platform>\S+).+"
        r"Version\s+(?P<version>\S+)",
        re.MULTILINE
    )

    def execute(self):
        v = self.cli("show /sys version")
        match = self.rx_version.search(v)
        return {
            "vendor": "f5",
            "platform": match.group("product"),
            "version": match.group("version")
        }
