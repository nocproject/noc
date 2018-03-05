# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Rotek.BT.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Rotek.BT.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def execute(self):
        interfaces = []
        # Try SNMP first
        if self.has_snmp():
            try:
                for v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.1", cached=True):
                    ifindex = v[1]
                    name = self.snmp.get("1.3.6.1.2.1.2.2.1.2." + str(ifindex))
                    mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6." + str(ifindex))
                    a_status = self.snmp.get("1.3.6.1.2.1.2.2.1.7." + str(ifindex))
                    o_status = self.snmp.get("1.3.6.1.2.1.2.2.1.8." + str(ifindex))
                    if a_status == 7:
                        admin_status = True
                    else:
                        admin_status = False
                    if o_status == 1:
                        oper_status = True
                    else:
                        oper_status = False
                    # print repr("%s\n" % admin_status)
                    interfaces += [{
                        "type": "physical",
                        "name": name,
                        "mac": mac,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "subinterfaces": [{
                            "name": name,
                            "mac": mac,
                            "snmp_ifindex": ifindex,
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "enabled_afi": ["BRIDGE"]
                        }]
                    }]
            except self.snmp.TimeOutError:
                pass
        interfaces += [{
            "type": "physical",
            "name": "st",
            "admin_status": True,
            "oper_status": True,
            "subinterfaces": [{
                "name": "st",
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"]
            }]
        }]
        return [{"interfaces": interfaces}]
