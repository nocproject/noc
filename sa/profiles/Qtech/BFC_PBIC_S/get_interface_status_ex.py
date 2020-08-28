# ---------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute_snmp(self, interfaces=None):
        result = []
        temp = self.snmp.get("1.3.6.1.3.55.1.2.1.0", cached=True)
        t_as = False
        t_os = False
        if temp != -104:
            t_as = True
            t_os = True
        result += [{"interface": "TempSensor 1", "admin_status": t_as, "oper_status": t_os}]
        for v in self.snmp.getnext("1.3.6.1.3.55.1.3.1.1", max_retries=3, cached=True):
            name = v[1]
            admin_status = False
            oper_status = False
            descr = self.snmp.get("1.3.6.1.3.55.1.3.1.2.%s" % name)
            status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % name)
            invert = self.snmp.get("1.3.6.1.3.55.1.3.1.3.%s" % name)
            if descr in [0, 3, 9, 10]:
                if invert == 0 and status == 0:
                    admin_status = True
                    oper_status = True
                elif invert == 1 and status == 1:
                    admin_status = True
                    oper_status = True
            else:
                if status > 0:
                    admin_status = True
                    oper_status = True
            result += [
                {"interface": name, "admin_status": admin_status, "oper_status": oper_status}
            ]
        result += [
            {
                "interface": "eth0",
                "admin_status": True,
                "oper_status": True,
                "full_duplex": True,
                "in_speed": 10000,
                "out_speed": 10000,
            }
        ]
        return result
