# ---------------------------------------------------------------------
# Telecom.CPE.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "Telecom.CPE.get_interface_status"
    interface = IGetInterfaceStatus

    def execute_snmp(self, interface=None, **kwargs):
        # Get interface status
        r = []
        for i, n, s in self.snmp.join([mib["IF-MIB::ifName"], mib["IF-MIB::ifOperStatus"]]):
            iface = self.profile.convert_interface_name(n)
            if interface and interface == iface:
                return [{"interface": iface, "status": int(s) == 1}]
            r += [{"interface": iface, "status": int(s) == 1}]
        return r
