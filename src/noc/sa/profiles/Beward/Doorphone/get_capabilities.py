# ---------------------------------------------------------------------
# Beward.Doorphone.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_snmp_error
from noc.core.mib import mib
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Beward.Doorphone.get_capabilities"
    cache = True

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        result = self.snmp.get(mib["LLDP-MIB::lldpLocChassisIdSubtype", 0])
        return is_int(result) and result >= 1
