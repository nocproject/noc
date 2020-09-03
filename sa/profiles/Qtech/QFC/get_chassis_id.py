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

    def check_oid(self):
        if self.is_lite:
            return 103
        return 102

    def execute_snmp(self):
        base = self.snmp.get("1.3.6.1.4.1.27514.%s.0.4.0" % self.check_oid())
        if base:
            return [{"first_chassis_mac": base, "last_chassis_mac": base}]
