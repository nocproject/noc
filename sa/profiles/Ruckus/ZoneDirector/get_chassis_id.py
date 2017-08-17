# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.ZoneDirector.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Ruckus.ZoneDirector.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"\s*MAC\sAddress=\s+(?P<id>\S+).+\n", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show sysinfo")
        match = self.re_search(self.rx_mac, v)
        base = match.group("id")
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }]
