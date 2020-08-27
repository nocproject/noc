# ----------------------------------------------------------------------
# Qtech.BFC-PBIC-S.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
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
        10: "Вход сигнала ИБП (Питание от сети)",
    }

    def execute_snmp(self):
        interfaces = []
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
                admin_status = False
                oper_status = False
            iface = {
                "type": "physical",
                "name": name,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "snmp_ifindex": name,
                "description": self.PORT_TYPE.get(descr),
                "subinterfaces": [
                    {
                        "name": name,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "snmp_ifindex": name,
                    }
                ],
            }
            interfaces += [iface]
        ip = self.credentials.get("address", "")
        ip = ip + "/" + str(32)
        ip_list = [ip]
        mac = self.snmp.get("1.3.6.1.3.55.1.2.2.0")
        iface = {
            "type": "physical",
            "name": "eth0",
            "admin_status": True,
            "oper_status": True,
            "mac": mac,
            "snmp_ifindex": 10,
            "subinterfaces": [
                {
                    "name": "eth0",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": mac,
                    "ipv4_addresses": ip_list,
                    "snmp_ifindex": 10,
                    "enabled_afi": ["BRIDGE", "IPv4"],
                }
            ],
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
