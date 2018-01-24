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
        for v in self.snmp.getnext("1.3.6.1.3.55.1.3.1.1", cached=True):
            name = v[1]
            status = self.snmp.get("1.3.6.1.3.55.1.3.1.4.%s" % name)
            if status == 0:
                admin_status = True
                oper_status = True
            else:
                admin_status = False
                oper_status = False
            iface = {
                "type": "physical",
                "name": name,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "snmp_ifindex": name,
                "subinterfaces": [{
                    "name": name,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "snmp_ifindex": name
                }]
            }
            interfaces += [iface]
        print self.credentials.get("address", "")
        ip = self.credentials.get("address", "")
        ip = ip + '/' + str(32)
        ip_list = [ip]
        iface = {
            "type": "physical",
            "name": "eth0",
            "admin_status": True,
            "oper_status": True,
            "mac": self.snmp.get("1.3.6.1.3.55.1.2.2.0"),
            "snmp_ifindex": 10,
            "subinterfaces": [{
                "name": "eth0",
                "admin_status": True,
                "oper_status": True,
                "mac": self.snmp.get("1.3.6.1.3.55.1.2.2.0"),
                "ipv4_addresses": ip_list,
                "snmp_ifindex": 10,
                "enabled_afi": ['BRIDGE', 'IPv4']
            }]
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
