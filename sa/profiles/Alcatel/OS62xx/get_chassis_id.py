# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("show system", cached=True)
        match = self.rx_mac.search(v)
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
