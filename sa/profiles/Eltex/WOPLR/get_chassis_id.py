# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.WOPLR.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.WOPLR.get_chassis_id"
    interface = IGetChassisID

    def execute_cli(self, **kwargs):
        d = self.cli("monitoring information", cached=True)
        for line in d.splitlines():
            r = line.split(":", 1)
            if r[0].strip() == "factory-wan-mac":
                mac = r[1].strip()
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
