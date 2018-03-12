# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_capabilities
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
    name = "DLink.DxS.get_capabilities"

    rx_lldp = re.compile(r"LLDP Status\s+: Enabled?")
    rx_stp = re.compile(r"STP Status\s+: Enabled?")
    rx_oam = re.compile(r"^\s*OAM\s+: Enabled", re.MULTILINE)
    rx_stack = re.compile(r"^\s*(?P<box_id>\d+)\s+", re.MULTILINE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return self.rx_lldp.search(cmd) is not None

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

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("show stp")
        return self.rx_stp.search(cmd) is not None

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has OAM supported
        """
        cmd = self.cli("show ethernet_oam ports status")
        return self.rx_oam.search(cmd) is not None

    def execute_platform_cli(self, caps):
        try:
            cmd = self.cli("show stack_device")
            s = []
            for match in self.rx_stack.finditer(cmd):
                s += [match.group("box_id")]
            if s:
                caps["Stack | Members"] = len(s) if len(s) != 1 else 0
                caps["Stack | Member Ids"] = " | ".join(s)
        except self.CLISyntaxError:
            pass
