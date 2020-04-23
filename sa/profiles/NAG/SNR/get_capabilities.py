# ---------------------------------------------------------------------
# NAG.SNR.get_capabilities
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
    name = "NAG.SNR.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP has been enabled globally?")
    rx_stack = re.compile(r"-+member :(?P<id>\d+)-+")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled on SNR
        """
        cmd = self.cli("show lldp", ignore_errors=True)
        return self.rx_lldp_en.search(cmd) is not None

    def execute_platform_cli(self, caps):
        try:
            s = []
            cmd = self.cli("show slot")
            for match in self.rx_stack.finditer(cmd):
                i = match.group("id")
                s += [i]
            if s:
                caps["Stack | Members"] = len(s) if len(s) != 1 else 0
                caps["Stack | Member Ids"] = " | ".join(s)
        except Exception:
            pass
