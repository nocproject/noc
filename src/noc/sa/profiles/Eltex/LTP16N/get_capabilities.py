# ---------------------------------------------------------------------
# Eltex.LTP16N.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules

# NOC modules
from noc.sa.profiles.Eltex.LTP.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.LTP16N.get_capabilities"
    cache = True

    def get_cpe_num(self):
        return len(self.scripts.get_cpe())

    def execute_platform_cli(self, caps):
        cpe_num = self.get_cpe_num()
        if cpe_num:
            caps["DB | CPEs"] = cpe_num
            caps["Network | PON | OLT"] = True

    def execute_platform_snmp(self, caps):
        cpe_num = self.get_cpe_num()
        if cpe_num:
            caps["DB | CPEs"] = cpe_num
            caps["Network | PON | OLT"] = True

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled on Eltex
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
        if r:
            return True
