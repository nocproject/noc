# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSN.hiX56xx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "NSN.hiX56xx.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s+[0-9a-f]+\.(?P<mac>[0-9a-f]{12})", re.MULTILINE)

    def execute(self):
        v = self.cli("show stp")
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
