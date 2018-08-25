# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SMB.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Cisco.SMB.get_capabilities"

    rx_stp = re.compile("Spanning tree enabled mode \S+STP")

    def has_cdp_snmp(self):
        """
        Check box has cdp enabled
        """
        # ciscoCdpMIB::cdpGlobalRun
        r = self.snmp.get("1.3.6.1.4.1.9.9.23.1.3.1.0")
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
        if match:
            return True
        return False

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp configuration")
        return "LLDP state: Enabled" in r
