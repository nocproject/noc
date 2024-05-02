# ---------------------------------------------------------------------
# Generic.get_snmp_availability
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetsnmpavailability import IGetSNMPAvailability
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_snmp_availability"
    interface = IGetSNMPAvailability
    requires = []

    SNMP_OID_CHECK = mib["SNMPv2-MIB::sysObjectID", 0]
    SNMP_CHECK_COUNT = 3
    SNMP_CHECK_TIMEOUT = 1

    def execute_snmp(self, **kwargs):
        N = 0
        while N < self.SNMP_CHECK_COUNT:
            N += 1
            try:
                v = self.snmp.get(oids=self.SNMP_OID_CHECK, timeout=self.SNMP_CHECK_TIMEOUT)
                if v:
                    return True
            except (self.snmp.TimeOutError, self.snmp.FatalTimeoutError, self.snmp.SNMPError):
                pass
        return False
