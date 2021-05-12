# ---------------------------------------------------------------------
# Ttronics.KUB.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_snmp_error


class Script(BaseScript):
    name = "Ttronics.KUB.get_capabilities"

    @false_on_snmp_error
    def check_ups_connected(self):
        return self.snmp.get("1.3.6.1.4.1.51315.1.29.0") != 0

    @false_on_snmp_error
    def check_elmeter_connected(self):
        return bool(self.snmp.get("1.3.6.1.4.1.51315.1.26.0"))

    def execute_platform_snmp(self, caps):
        caps["Sensor | Controller"] = True
        if not self.is_femto:
            r = self.check_ups_connected()
            if r is not None:
                caps["Sensor | UPS"] = r
            r = self.check_elmeter_connected()
            if r is not None:
                caps["Sensor | elMeter"] = r
