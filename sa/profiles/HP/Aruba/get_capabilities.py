# ---------------------------------------------------------------------
# HP.Aruba.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.Aruba.get_capabilities"
    rx_lldp = re.compile(r"LLDP Enabled\s+:\s*Yes")
    rx_stp = re.compile(r"Spanning tree status\s+:\s*Enabled")

    GET_SNMP_TABLE_IDX = {
        "SNMP | HOST-RESOURCES-MIB | CPU Cores | Idx": mib["HOST-RESOURCES-MIB::hrProcessorFrwID"]
    }

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp configuration")
        return bool(self.rx_lldp.search(cmd))

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled on Eltex
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
        if r:
            return True

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree")
        return bool(self.rx_stp.search(cmd))

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show lacp configuration")
        return r
