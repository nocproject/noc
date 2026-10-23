# ---------------------------------------------------------------------
# Qtech.QFC.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Qtech.QFC.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_snmp(self):
        if self.is_lite:
            base = self.snmp.get("1.3.6.1.4.1.27514.103.0.4.0")
        else:
            base = self.snmp.get("1.3.6.1.4.1.27514.102.0.4.0")
        if base:
            return [{"first_chassis_mac": base, "last_chassis_mac": base}]
