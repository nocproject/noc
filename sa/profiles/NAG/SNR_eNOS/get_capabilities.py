# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP Tx enabled")
    rx_stack = re.compile(r"-+member :(?P<id>\d+)-+")

    def get_lldp_cli(self):
        """
        Check box has lldp enabled on SNR
        """
        try:
            cmd = self.cli("show lldp port xe1")
        except self.CLISyntaxError:
            # FoxGate CLI
            cmd = self.cli("show lldp interface")
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
