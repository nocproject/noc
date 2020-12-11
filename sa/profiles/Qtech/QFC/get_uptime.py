# ---------------------------------------------------------------------
# Qtech.QFC.get_uptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetuptime import IGetUptime
from noc.core.validators import is_float


class Script(BaseScript):
    """
    Returns system uptime in seconds
    """

    name = "Qtech.QFC.get_uptime"
    interface = IGetUptime
    requires = []

    def check_oid(self):
        if self.is_lite:
            return "103.0.12.0"
        return "102.0.19.0"

    def execute(self):
        if self.has_snmp():
            try:
                su = self.snmp.get("1.3.6.1.4.1.27514.%s" % self.check_oid())
                # DES-1210-28/ME/B3 fw 10.04.B020 return 'VLAN-1002'
                if is_float(su):
                    return float(su) // 100.0
            except (self.snmp.TimeOutError, self.snmp.SNMPError):
                pass
        return None
