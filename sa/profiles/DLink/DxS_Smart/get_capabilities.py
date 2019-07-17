# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_capabilities"

    rx_lldp = re.compile(r"LLDP Status\s+: Enabled?")

    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        # swL2DevCtrlLLDPState can only get from l2mgmt-mib
        # LLDP-MIB::lldpStatsRemTablesInserts.0
        try:
            r = self.snmp.get("1.0.8802.1.1.2.1.2.2.0")
            if r > 0:
                return True
        except self.snmp.TimeOutError:
            return False
