# ---------------------------------------------------------------------
# Qtech.QFC.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_snmp_error
from noc.core.snmp.error import SNMPError


class Script(BaseScript):
    name = "Qtech.QFC.get_capabilities"

    SNMP_GET_CHECK_OID = "1.3.6.1.4.1.27514."
    CHECK_OID = ["102.0.1", "103.0.1"]

    def check_snmp_get(self, oid, version=None):
        """
        Check SNMP GET response to oid
        """
        if self.credentials.get("snmp_ro"):
            for value in self.CHECK_OID:
                try:
                    r = self.snmp.get(oid + value, version=version)
                    return r is not None
                except (self.snmp.TimeOutError, SNMPError):
                    pass
        return False

    @false_on_snmp_error
    def check_ups_connected(self):
        if not self.is_lite:
            return None
        return bool(self.snmp.get("1.3.6.1.4.1.27514.103.0.13.0"))

    @false_on_snmp_error
    def check_elmeter_connected(self):
        if not self.is_lite:
            return bool(self.snmp.get("1.3.6.1.4.1.27514.102.0.20.0"))
        return bool(self.snmp.get("1.3.6.1.4.1.27514.103.0.27.0"))

    def execute_platform_snmp(self, caps):
        r = self.check_ups_connected()
        if r is not None:
            caps["Sensor | UPS"] = r
        r = self.check_elmeter_connected()
        if r is not None:
            caps["Sensor | elMeter"] = r
        caps["Sensor | Controller"] = True
