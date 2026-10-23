# Qtech.QOS.get_capabilities
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
    name = "Qtech.QOS.get_capabilities"

    rx_lldp = re.compile(r"LLDP enable status:\s+enable")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp local config")
        return bool(self.rx_lldp.search(cmd))

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        try:
            r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
            if r:
                return True
        except self.snmp.TimeOutError:
            return False
