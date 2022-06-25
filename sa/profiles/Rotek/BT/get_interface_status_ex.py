# ---------------------------------------------------------------------
# Rotek.BT.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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

        return result
