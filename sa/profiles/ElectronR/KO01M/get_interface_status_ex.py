# ---------------------------------------------------------------------
# ElectronR.KO01M.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "ElectronR.KO01M.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute_snmp(self, interfaces=None):
        index = [1, 2, 3, 4, 5]
        result = []
        temp = self.snmp.get("1.3.6.1.4.1.35419.20.1.140.0", cached=True)
        t_st = False
        if temp != -104:
            t_st = True
        result += [{"interface": "Temperature", "admin_status": t_st, "oper_status": t_st}]
        impulse = self.snmp.get("1.3.6.1.4.1.35419.20.1.160.0", cached=True)
        i_st = False
        if impulse != 0:
            i_st = True
        result += [{"interface": "Pulse", "admin_status": i_st, "oper_status": i_st}]
        for ifindex in index:
            status = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % ifindex)
            if status == 0:
                s_status = False
            else:
                s_status = True
            result += [{"interface": ifindex, "admin_status": s_status, "oper_status": s_status}]
        result += [
            {
                "interface": "eth0",
                "admin_status": True,
                "oper_status": True,
                "full_duplex": False,
                "in_speed": 10000,
                "out_speed": 10000,
            }
        ]
        return result
