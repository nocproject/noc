# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_license
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlicense import IGetLicense


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_license"
    interface = IGetLicense

    rx_line = re.compile(
        r"^(?P<name>.+)\s+license\s+(?P<inst>.+)\n", re.MULTILINE)
    rx_count = re.compile(r"(?P<count>\d+)\s+\S+$")

    def execute(self):
        r = {}
        for match in self.rx_line.finditer(self.cli("show license")):
            inst = match.group("inst").strip()
            if "is not set" in inst:
                r[match.group("name")] = 0
            else:
                match1 = self.rx_count.search(inst)
                if match1:
                    r[match.group("name")] = int(match1.group("count"))
                else:
                    r[match.group("name")] = 1
        return r
