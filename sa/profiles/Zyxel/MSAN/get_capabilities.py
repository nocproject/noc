# ---------------------------------------------------------------------
# Zyxel.MSAN.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Zyxel.MSAN.get_capabilities"
    CHECK_SNMP_GETNEXT = {"SNMP | MIB | ADSL-MIB": mib["ADSL-LINE-MIB::adslMIB"]}
    rx_stp_active = re.compile(r"status\s+:\s+enabled", re.MULTILINE)

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("switch mstp show", cached=True)
        return bool(self.rx_stp_active.search(r))

    @false_on_snmp_error
    def has_stack_snmp(self):
        """
        Check stack members
        :return:
        """
        r = []
        stack_num = 0
        for oid, slot_module_type in self.snmp.getnext("1.3.6.1.4.1.890.1.5.13.1.1.3.1.7"):
            if slot_module_type == 2:  # empty(1), up(2), down(3), testing(4), standby(5)
                stack_num = oid.split(".")[-1]
                r += [str(stack_num)]
        return r

    def execute_platform_snmp(self, caps):
        s = self.has_stack_snmp()
        if s:
            caps["Stack | Members"] = len(s) if len(s) >= 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
