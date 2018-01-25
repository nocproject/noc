# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ElectronR.KO01M.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "ElectronR.KO01M.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    requires = []

    def execute(self):
        i = [1, 2, 3, 4, 5]
        result = []
        for ii in i:
            status = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % ii)
            if status == 0:
                admin_status = False
                oper_status = False
            else:
                admin_status = True
                oper_status = True
            r = {
                'interface': ii,
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
