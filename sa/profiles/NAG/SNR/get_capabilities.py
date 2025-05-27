# ---------------------------------------------------------------------
# NAG.SNR.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_snmp_error
from noc.core.mib import mib
from noc.core.validators import is_int


class Script(BaseScript):
    name = "NAG.SNR.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP has been enabled globally?")
    rx_stack = re.compile(r"-+member :(?P<id>\d+)-+")

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpLocChassisIdSubtype", 0])
        return is_int(r) and r >= 1

    @false_on_snmp_error
    def has_stp_snmp(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        r = self.snmp.getnext(mib["BRIDGE-MIB::dot1dStpPortEnable"], bulk=False)
        # if value == 1:
        return any(x[1] for x in r)

    def get_lldp_cli(self):
        """
        Check box has lldp enabled on SNR
        """
        try:
            cmd = self.cli("show lldp")
        except self.CLISyntaxError:
            # FoxGate CLI
            cmd = self.cli("show lldp interface", cached=True)
            return "System LLDP: enable" in cmd, True
        return self.rx_lldp_en.search(cmd) is not None, False

    def get_stack_members(self):
        s = []
        try:
            cmd = self.cli("show slot")
        except self.CLISyntaxError:
            return
        for match in self.rx_stack.finditer(cmd):
            i = match.group("id")
            s += [i]
        return s

    def execute_platform_cli(self, caps):
        members = self.get_stack_members()
        if members:
            caps["Stack | Members"] = len(members) if len(members) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(members)
        has_lldp, foxgate_cli = self.get_lldp_cli()
        if has_lldp:
            caps["Network | LLDP"] = True
        if foxgate_cli:
            caps["NAG | SNR | CLI | Old"] = True
