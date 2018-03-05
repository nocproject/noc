# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                base = self.snmp.get("1.3.6.1.2.1.2.2.1.6.4")
                return [{
                    "first_chassis_mac": base,
                    "last_chassis_mac": base
                }]
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
