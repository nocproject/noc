# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.RG_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Eltex.RG.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self, interface=None):
        if self.has_snmp():
            s = self.snmp.get("1.3.6.1.2.1.2.2.1.6.2")
            return {"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}
        else:
            raise self.NotSupportedError
