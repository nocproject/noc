# ---------------------------------------------------------------------
# Cisco.SMB.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Cisco.SMB.get_capabilities"

    rx_stp = re.compile(r"Spanning tree enabled mode \S+STP")

    def has_cdp_snmp(self):
        """
        Check box has cdp enabled
        """
        r = self.snmp.get(mib["CISCO-CDP-MIB::cdpGlobalRun", 0])
        return r == 1

    @false_on_cli_error
    def has_cdp_cli(self):
        """
        Check box has cdp enabled
        """
        r = self.cli("show cdp")
        return "CDP is globally enabled" in r

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree")
        match = self.rx_stp.search(r)
        return bool(match)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp configuration")
        return "LLDP state: Enabled" in r
