# ---------------------------------------------------------------------
# Qtech.QFC.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
        return [
            {
                "interface": "eth0",
                "admin_status": True,
                "oper_status": True,
                "full_duplex": False,
                "in_speed": 10000,
                "out_speed": 10000,
            }
        ]
