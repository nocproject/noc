# ---------------------------------------------------------------------
# Beward.Doorphone.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "Beward.Doorphone.get_interface_status"
    interface = IGetInterfaceStatus

    def execute_snmp(self, interface=None, **kwargs):
        result = []
        for _, name, status in self.snmp.join([mib["IF-MIB::ifName"], mib["IF-MIB::ifOperStatus"]]):
            iface = self.profile.convert_interface_name(name)
            if interface and interface == iface:
                return [{"interface": iface, "status": int(status) == 1}]
            result += [{"interface": iface, "status": int(status) == 1}]
        return result
