# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Qtech.QFC_PBIC_Lite.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Qtech.QFC_PBIC_Lite.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def execute(self):
        interfaces = []
        interfaces += [{
            "type": "physical",
            "name": "eth0",
            "admin_status": True,
            "oper_status": True,
            "snmp_ifindex": 1,
            "subinterfaces": [{
                "name": "eth0",
                "admin_status": True,
                "oper_status": True,
                "snmp_ifindex": 1,
                "enabled_afi": ["BRIDGE"]
            }]
        }]
        return [{"interfaces": interfaces}]
