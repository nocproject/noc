# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QFC_PBIC_Lite.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Qtech.QFC_PBIC_Lite.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                base = self.snmp.get("1.3.6.1.4.1.27514.101.1.2")
                if base:
                    return [{
                        "first_chassis_mac": base,
                        "last_chassis_mac": base
                    }]
            except self.snmp.TimeOutError:
                pass
            except self.snmp.SNMPError:
                pass
