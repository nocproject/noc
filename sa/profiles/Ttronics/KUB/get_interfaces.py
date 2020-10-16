# ----------------------------------------------------------------------
# Ttronics.KUB.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Ttronics.KUB.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def status(self, index):
        return self.snmp.get("1.3.6.1.4.1.51315.1.%s.0" % index, cached=True)

    def execute_snmp(self):
        interfaces = []

        for sensor in self.profile.SENSORS_TYPE.keys():
            status = self.status(sensor)
            s_type = self.snmp.get(
                "1.3.6.1.4.1.51315.1.%s.0" % self.profile.SENSORS_TYPE.get(sensor), cached=True
            )
            s_status = False
            if status == 0:
                s_status = True
            print(sensor)
            interfaces += [
                {
                    "type": "physical",
                    "name": "%s/%s" % (s_type, sensor - 2) if s_type in [0, 1, 2] else s_type,
                    "admin_status": s_status,
                    "oper_status": s_status,
                    "snmp_ifindex": sensor,
                    "description": "%s %s" % (self.profile.PORT_TYPE.get(s_type), sensor - 2)
                    if s_type in [0, 1, 2]
                    else self.profile.PORT_TYPE.get(s_type),
                    "subinterfaces": [],
                }
            ]
        for sensor2 in self.profile.SENSORS_TYPE2.keys():
            status2 = self.status(sensor)
            s2_status = False
            if sensor2 == 1:
                if status2 != -128:
                    s2_status = True
            else:
                if status2 == 0:
                    s2_status = True
            interfaces += [
                {
                    "type": "physical",
                    "name": self.profile.SENSORS_TYPE2.get(sensor2),
                    "admin_status": s2_status,
                    "oper_status": s2_status,
                    "snmp_ifindex": sensor2,
                    "description": "Вход датчика температуры"
                    if sensor2 == 1
                    else self.profile.PORT_TYPE.get(sensor2),
                    "subinterfaces": [],
                }
            ]
        mac = self.snmp.get("1.3.6.1.4.1.51315.1.20.0")
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
