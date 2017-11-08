# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.MA4000.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s+MAC address:\s+(?P<mac>\S+)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        for i in ["1", "2"]:
            c = self.cli("show system information %s" % i, cached=True)
            match = self.rx_mac.search(c)
            if match:
                r += [{
                    "first_chassis_mac": match.group("mac"),
                    "last_chassis_mac": match.group("mac")
                }]
        return r
