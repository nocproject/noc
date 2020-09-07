# ---------------------------------------------------------------------
# Rotek.BT.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.BT.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute_snmp(self, interfaces=None):
        result = []
        try:
            ifindex = self.snmp.get("1.3.6.1.2.1.2.2.1.1.1")
            name = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
            a_status = self.snmp.get(mib["IF-MIB::ifAdminStatus", ifindex])
            o_status = self.snmp.get(mib["IF-MIB::ifOperStatus", ifindex])
            result += [{"interface": name, "admin_status": a_status, "oper_status": o_status}]
        except Exception:
            result += [{"interface": "st", "admin_status": True, "oper_status": True}]
        for index in self.profile.PORT_TYPE.keys():
            s_status = 0
            status = self.snmp.get("1.3.6.1.4.1.41752.5.15.1.%s.0" % index)
            if index == 1 and int(status) == 0:
                s_status = 1
            elif index == 2 and (-55 < float(status) < 600):
                s_status = 1
            elif index in [3, 5] and float(status) > 0:
                s_status = 1
            elif index == 9 and int(status) == 0:
                s_status = 1
            result += [
                {
                    "interface": self.profile.IFACE_NAME.get(index),
                    "admin_status": s_status,
                    "oper_status": s_status,
                }
            ]

        return result
