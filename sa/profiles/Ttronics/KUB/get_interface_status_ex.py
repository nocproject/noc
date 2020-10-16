# ---------------------------------------------------------------------
# Ttronics.KUB.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Ttronics.KUB.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute_snmp(self, interfaces=None):
        result = []
        for sensor in self.profile.SENSORS_TYPE.keys():
            status = self.snmp.get("1.3.6.1.4.1.51315.1.%s.0" % sensor, cached=True)
            s_type = self.snmp.get(
                "1.3.6.1.4.1.51315.1.%s.0" % self.profile.SENSORS_TYPE.get(sensor), cached=True
            )
            s_status = False
            if status == 0:
                s_status = True
            result += [
                {
                    "interface": "%s/%s" % (s_type, sensor - 2) if s_type in [0, 1, 2] else s_type,
                    "admin_status": s_status,
                    "oper_status": s_status,
                }
            ]
        for sensor2 in self.profile.SENSORS_TYPE2.keys():
            status2 = self.snmp.get("1.3.6.1.4.1.51315.1.%s.0" % sensor2, cached=True)
            s2_status = False
            if sensor2 == 1:
                if status2 != -128:
                    s2_status = True
            else:
                if status2 == 0:
                    s2_status = True
            result += [
                {
                    "interface": self.profile.SENSORS_TYPE2.get(sensor2),
                    "admin_status": s2_status,
                    "oper_status": s2_status,
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
