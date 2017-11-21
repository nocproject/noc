# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SMB.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Cisco.SMB.get_capabilities"

    def has_cdp_snmp(self):
        """
        Check box has cdp enabled
        """
        # ciscoCdpMIB::cdpGlobalRun
        r = self.snmp.get("1.3.6.1.4.1.9.9.23.1.3.1.0")
        return r == 1

    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        # rlLldpEnabled
        r = self.snmp.get("1.3.6.1.4.1.9.6.1.101.110.1.1.1.0")
        return r == 1

    def has_stp_snmp(self):
        """
        Check box has stp enabled
        """
        # rldot1dStpEnable
        r = self.snmp.get("1.3.6.1.4.1.9.6.1.101.57.2.3.0")
        return r == 1
