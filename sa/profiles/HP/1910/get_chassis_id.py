# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.1910.get_chassis_id
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
    name = "HP.1910.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^MAC_ADDRESS\s+:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("display device manuinfo", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}