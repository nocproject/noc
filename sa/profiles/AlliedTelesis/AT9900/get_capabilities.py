# ---------------------------------------------------------------------
# AlliedTelesis.AT9900.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_capabilities"

    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        for v, r in self.snmp.getnext(mib["LLDP-MIB::lldpPortConfigAdminStatus"], bulk=False):
            if r != 4:
                return True
        return False

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show config dynamic", ignore_errors=True)
        return "enable lldp" in cmd
