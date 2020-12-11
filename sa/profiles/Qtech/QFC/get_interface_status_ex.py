# ---------------------------------------------------------------------
# Qtech.QFC.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Qtech.QFC.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute_snmp(self, interfaces=None):
        result = []
        if self.is_lite:
            for ifindex in self.profile.LITE_PORT_TYPE.keys():
                s_status = 0
                status = self.snmp.get("1.3.6.1.4.1.27514.103.0.%s" % ifindex)
                if ifindex in [5, 6, 7, 13] and status == 1:
                    s_status = 1
                elif ifindex in [8, 9] and -55 < status < 600:
                    s_status = 1
                elif ifindex == 27 and status > 0:
                    s_status = 1
                result += [
                    {
                        "interface": self.profile.LITE_IFACE_NAME.get(ifindex),
                        "admin_status": s_status,
                        "oper_status": s_status,
                    }
                ]
        else:
            for ifindex in self.profile.LIGHT_PORT_TYPE.keys():
                s_status = 0
                status = self.snmp.get("1.3.6.1.4.1.27514.102.0.%s" % ifindex)
                if ifindex in [5, 6, 7, 8, 9, 10] and status == 1:
                    s_status = 1
                elif ifindex in [13, 14] and -55 < status < 600:
                    s_status = 1
                elif ifindex == 12 and status > 0:
                    s_status = 1
                elif ifindex == 29 and int(status) > 0:
                    s_status = 1
                result += [
                    {
                        "interface": self.profile.LIGHT_IFACE_NAME.get(ifindex),
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
