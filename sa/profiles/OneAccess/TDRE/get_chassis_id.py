# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "OneAccess.TDRE.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"macAddress = (?P<mac>\S+)")

    def execute(self):
        self.cli("SELGRP Status")
        match = self.rx_mac.search(self.cli("GET bridge/bridgeGroup/macAddress"))
        return [{"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}]
