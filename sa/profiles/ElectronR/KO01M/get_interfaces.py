# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ElectronR.KO01M.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "ElectronR.KO01M.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def execute_snmp(self):
        i = [1, 2, 3, 4, 5]
        interfaces = []
        for ii in i:
            status = self.snmp.get("1.3.6.1.4.1.35419.20.1.10%s.0" % ii)
            if status == 0:
                admin_status = False
                oper_status = False
            else:
                admin_status = True
                oper_status = True
            iface = {
                "type": "physical",
                "name": ii,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "snmp_ifindex": ii,
                "subinterfaces": [{
                    "name": ii,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "snmp_ifindex": ii
                }]
            }
            interfaces += [iface]
        ip = self.snmp.get("1.3.6.1.4.1.35419.1.1.3.0")
        m = self.snmp.get("1.3.6.1.4.1.35419.1.1.4.0")
        mask = str(IPv4.netmask_to_len(m))
        ip = ip + '/' + mask
        ip_list = [ip]
        iface = {
            "type": "physical",
            "name": "eth0",
            "admin_status": True,
            "oper_status": True,
            "mac": self.snmp.get("1.3.6.1.4.1.35419.1.1.6.0"),
            "snmp_ifindex": 10,
            "subinterfaces": [{
                "name": "eth0",
                "admin_status": True,
                "oper_status": True,
                "mac": self.snmp.get("1.3.6.1.4.1.35419.1.1.6.0"),
                "ipv4_addresses": ip_list,
                "snmp_ifindex": 10,
                "enabled_afi": ['BRIDGE', 'IPv4']
            }]
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
