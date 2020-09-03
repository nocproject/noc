# ---------------------------------------------------------------------
# Qtech.QFC.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
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
