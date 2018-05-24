# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.TAU.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Eltex.TAU.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        c = self.cli("show hwaddr")
        s = c.split(":", 1)[1].strip()
        return {"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}
