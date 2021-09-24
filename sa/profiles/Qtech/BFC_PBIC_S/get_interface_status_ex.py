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
        t_st = False
        if -55 < temp < 600:
            t_st = True
        result += [{"interface": 21, "admin_status": t_st, "oper_status": t_st}]
        for oid, value in self.snmp.getnext("1.3.6.1.3.55.1.3.1.1", max_retries=3, cached=True):
            s_status = False
            battery = False
            descr = self.snmp.get("1.3.6.1.3.55.1.3.1.2.%s" % value)
            try:
                status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % value)
            except self.snmp.SNMPError:
                status = None
            if descr in [0, 3]:
                invert = self.snmp.get("1.3.6.1.3.55.1.3.1.3.%s" % value)
                if invert == 0 and status == 0:
                    s_status = True
                elif invert == 1 and status == 1:
                    s_status = True
            elif descr in [9, 10]:
                invert = self.snmp.get("1.3.6.1.3.55.1.3.1.3.%s" % value)
                if descr == 9:
                    if invert == 0 and status == 0:
                        s_status = True
                        battery = True
                    elif invert == 1 and status == 1:
                        s_status = True
                        battery = True
                    elif invert == 0 and status == 1:
                        s_status = True
                        battery = True
                    elif invert == 1 and status == 0:
                        s_status = True
                        battery = True
                if descr == 10:
                    if battery and invert == 0 and status == 0:
                        s_status = True
                    elif battery and invert == 1 and status == 1:
                        s_status = True
            elif status:
                s_status = True
            result += [
                {
                    "interface": "%s/%s" % (descr, value + 1) if descr == 0 else descr,
                    "admin_status": s_status,
                    "oper_status": s_status,
                }
            ]
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
