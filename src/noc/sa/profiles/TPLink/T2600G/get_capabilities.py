# ---------------------------------------------------------------------
# TPLink.T2600G.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_snmp_error
from noc.core.mib import mib
from noc.core.validators import is_int


class Script(BaseScript):
    name = "TPLink.T2600G.get_capabilities"

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpLocChassisIdSubtype", 0])
        return is_int(r) and r >= 1
