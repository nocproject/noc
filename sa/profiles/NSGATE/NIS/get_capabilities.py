# ---------------------------------------------------------------------
# NSGATE.NIS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "NSGATE.NIS.get_capabilities"

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled on Eltex
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
        if r:
            return True

    @false_on_snmp_error
    def has_stp_snmp(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        r = self.snmp.getnext(mib["BRIDGE-MIB::dot1dStpPortEnable"], bulk=False)
        # if value == 1:
        return any([x[1] for x in r])
