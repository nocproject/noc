# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_interface_status"
    interface = IGetInterfaceStatus

    def execute_snmp(self, interface=None):
        r = []
        for n, s in self.snmp.join_tables(mib["IF-MIB::ifName"], mib["IF-MIB::ifOperStatus"]):
            if n[:2] == "xe" or n[:2] == "ge":
                pass
            else:
                continue
            if interface:
                if n == interface:
                    r += [{"interface": n, "status": int(s) == 1}]
            else:
                r += [{"interface": n, "status": int(s) == 1}]
        return r
