# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_license
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modiles
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "f5.BIGIP.get_license"
    cache = True
    interface = IGetLicense

    rx_lic = re.compile(r"^(.+?)\s+(\d+)$")

    def execute(self):
        v = self.cli("b version")
        _, v = v.split("Enabled Features:\n")
        r = {}
        for l in v.splitlines():
            l = l.strip()
            if not l:
                continue
            match = self.rx_lic.match(l)
            if match:
                r[match.group(1)] = int(match.group(2))
            else:
                r[l] = True
        return r
