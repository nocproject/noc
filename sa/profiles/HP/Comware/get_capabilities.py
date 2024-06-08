# ---------------------------------------------------------------------
# HP.Comware.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.Comware.get_capabilities"

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        try:
            r = self.cli("display stp global | include Enabled")
            return "?STP" in r
        except self.CLISyntaxError:
            r = self.cli("display stp | include Enabled")
            return "?STP" in r

    @false_on_snmp_error
    def has_stp_snmp(self):
        """
        Check box has stp enabled on Eltex
        """
        # RADLAN-BRIDGEMIBOBJECTS-MIB::rldot1dStpEnable
        r = self.snmp.get("1.3.6.1.4.1.89.57.2.3.0")
        return r == 1

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        rx_lldp = re.compile(r"Global status of LLDP: Enable")
        cmd = self.cli("display lldp status | include Global")
        return rx_lldp.search(cmd) is not None

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has LLDP enabled
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
        if r:
            return True

    @false_on_cli_error
    def has_ndp(self):
        """
        Check box has NDP enabled
        """
        r = self.cli("display ndp")
        return "enabled" in r

    def execute_platform_cli(self, caps):
        if self.has_ndp():
            caps["Huawei | NDP"] = True
