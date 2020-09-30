# ----------------------------------------------------------------------
# ElectronR.KO01M.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "ElectronR.KO01M.get_interfaces"
    interface = IGetInterfaces

    def execute_snmp(self):
        i = [1, 2, 3, 4, 5]
        interfaces = []
        interfaces += [
            {
                "type": "physical",
                "name": "Temperature",
                "admin_status": True,
                "oper_status": True,
                "snmp_ifindex": 140,
                "subinterfaces": [],
            }
        ]
        interfaces += [
            {
                "type": "physical",
                "name": "Pulse",
                "admin_status": True,
                "oper_status": True,
                "snmp_ifindex": 160,
                "subinterfaces": [],
            }
        ]
        for ii in i:
            status = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % ii)
            interfaces += [
                {
                    "type": "physical",
                    "name": ii,
                    "admin_status": status,
                    "oper_status": status,
                    "snmp_ifindex": ii,
                    "subinterfaces": [],
                }
            ]
        interfaces += [
            {
                "type": "physical",
                "name": "eth0",
                "admin_status": True,
                "oper_status": True,
                "mac": self.snmp.get("1.3.6.1.4.1.35419.1.1.6.0"),
                "snmp_ifindex": 100,
                "subinterfaces": [],
            }
        ]
        return [{"interfaces": interfaces}]
