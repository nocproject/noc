# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Qtech.BFC-PBIC-S.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def execute(self):
        interfaces = []
        interfaces += [{
            "type": "physical",
            "name": "eth0",
            "snmp_ifindex": 1,
            "admin_status": True,
            "oper_status": True,
            "subinterfaces": [{
                "name": "eth0",
                "snmp_ifindex": 1,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"]
            }]
        }]
        return [{"interfaces": interfaces}]
