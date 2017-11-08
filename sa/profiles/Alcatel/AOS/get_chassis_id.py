# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.AOS.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Alcatel.AOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(r"MAC Address:\s+(?P<id>.*),",
                       re.IGNORECASE | re.MULTILINE)

    def execute(self):
        result = []
        v = self.cli("show CHASSIS")
        for match in self.rx_id.findall(v):
            result.append({
                "first_chassis_mac": match,
                "last_chassis_mac": match
            })

        return result
