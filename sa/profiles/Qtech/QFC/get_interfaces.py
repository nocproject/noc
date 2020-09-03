# ----------------------------------------------------------------------
# Qtech.QFC.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Qtech.QFC.get_interfaces"
    interface = IGetInterfaces

    def check_oid(self):
        if self.is_lite:
            return 103
        return 102

    def execute_snmp(self):
        interfaces = []
        for ifindex in self.profile.PORT_TYPE.keys():
            s_status = 0
            status = self.snmp.get("1.3.6.1.4.1.27514.%s.0.%s" % (self.check_oid(), ifindex))
            if ifindex in [5, 6, 13] and status == 1:
                s_status = 1
            elif ifindex in [8, 9] and status != -1000:
                s_status = 1
            elif ifindex == 27 and status > 0:
                s_status = 1
            interfaces += [
                {
                    "type": "physical",
                    "name": ifindex,
                    "admin_status": s_status,
                    "oper_status": s_status,
                    "snmp_ifindex": ifindex,
                    "description": self.profile.PORT_TYPE.get(ifindex),
                    "subinterfaces": [],
                }
            ]
        mac = self.snmp.get("1.3.6.1.4.1.27514.%s.0.4.0" % self.check_oid())
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
