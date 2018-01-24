# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute(self):
        result = []
        for v in self.snmp.getnext("1.3.6.1.3.55.1.3.1.1", cached=True):
            name = v[1]
            status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % name)
            if status == 0:
                admin_status = True
                oper_status = True
            else:
                admin_status = False
                oper_status = False
            r = {
                'interface': name,
                'admin_status': admin_status,
                'oper_status': oper_status
            }
            result += [r]
        r = {
            'interface': "eth0",
            'admin_status': True,
            'oper_status': True,
            'full_duplex': True,
            'in_speed': 10000,
            'out_speed': 10000
        }
        result += [r]
        return result
