# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Qtech.QSW2500.get_chassis_id"
    interface = IGetChassisID
    cache = True

    def execute_cli(self):
        ver = self.cli("show version", cached=True)
        match = self.profile.rx_ver.search(ver)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
