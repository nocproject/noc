# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# f5.BIGIP.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modiles
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
        for line in v.splitlines():
            line = line.strip()
            if not line:
                continue
            match = self.rx_lic.match(line)
            if match:
                r[match.group(1)] = int(match.group(2))
            else:
                r[line] = True
        return r
