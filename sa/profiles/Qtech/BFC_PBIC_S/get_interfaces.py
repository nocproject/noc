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

    PORT_TYPE = {
        0: "Дискретный вход",
        1: "Вход по напряжению",
        2: "Вход счетчика импульсов",
        3: "Вход датчика вибрации/удара",
        4: "Вход по сопротивлению",
        9: "Вход сигнала ИБП (Батарея разряжена)",
        10: "Вход сигнала ИБП (Питание от сети)"
    }

    def execute_snmp(self):
        interfaces = []
        temp = self.snmp.get("1.3.6.1.3.55.1.2.1.0", cached=True)
        t_as = False
        t_os = False
        if temp != -104:
            t_as = True
            t_os = True
        interfaces += [{
            "type": "physical",
            "name": "TempSensor 1",
            "admin_status": t_as,
            "oper_status": t_os,
            "snmp_ifindex": 21,
            "description": "Выносной датчик температуры 1",
            "subinterfaces": [],
        }]
        for v in self.snmp.getnext("1.3.6.1.3.55.1.3.1.1", max_retries=3, cached=True):
            name = v[1]
            admin_status = False
            oper_status = False
            descr = self.snmp.get("1.3.6.1.3.55.1.3.1.2.%s" % name)
            if descr in [0, 3, 9, 10]:
                status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % name)
                invert = self.snmp.get("1.3.6.1.3.55.1.3.1.3.%s" % name)
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
            interfaces += [{
                "type": "physical",
                "name": name,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "snmp_ifindex": name,
                "description": self.PORT_TYPE.get(descr),
                "subinterfaces": [],
            }]
        mac = self.snmp.get("1.3.6.1.3.55.1.2.2.0")
        interfaces += [{
            "type": "physical",
            "name": "eth0",
            "admin_status": True,
            "oper_status": True,
            "mac": mac,
            "snmp_ifindex": 100,
            "subinterfaces": [],
        }]
        return [{"interfaces": interfaces}]
