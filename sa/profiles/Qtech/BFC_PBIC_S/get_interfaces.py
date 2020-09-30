# ----------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def execute_snmp(self):
        interfaces = []
        temp = self.snmp.get("1.3.6.1.3.55.1.2.1.0", cached=True)
        t_st = False
        if -55 < temp < 600:
            t_st = True
        interfaces += [
            {
                "type": "physical",
                "name": 21,
                "admin_status": t_st,
                "oper_status": t_st,
                "snmp_ifindex": 21,
                "description": "Выносной датчик температуры",
                "subinterfaces": [],
            }
        ]
        for oid, value in self.snmp.getnext("1.3.6.1.3.55.1.3.1.1", max_retries=3, cached=True):
            s_status = False
            battery = False
            descr = self.snmp.get("1.3.6.1.3.55.1.3.1.2.%s" % value)
            status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % value)
            invert = self.snmp.get("1.3.6.1.3.55.1.3.1.3.%s" % value)
            if descr in [0, 3]:
                if invert == 0 and status == 0:
                    s_status = True
                elif invert == 1 and status == 1:
                    s_status = True
            elif descr in [9, 10]:
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
            else:
                if status > 0:
                    s_status = True
            interfaces += [
                {
                    "type": "physical",
                    "name": "%s/%s" % (descr, value + 1) if descr == 0 else descr,
                    "admin_status": s_status,
                    "oper_status": s_status,
                    "snmp_ifindex": value,
                    "description": "%s %s" % (self.profile.PORT_TYPE.get(descr), value + 1)
                    if descr == 0
                    else self.profile.PORT_TYPE.get(descr),
                    "subinterfaces": [],
                }
            ]
        mac = self.snmp.get("1.3.6.1.3.55.1.2.2.0")
        interfaces += [
            {
                "type": "physical",
                "name": "eth0",
                "admin_status": True,
                "oper_status": True,
                "mac": mac,
                "snmp_ifindex": 100,
                "subinterfaces": [],
            }
        ]
        return [{"interfaces": interfaces}]
