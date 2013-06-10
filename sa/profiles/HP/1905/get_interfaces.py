# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
import re
# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(noc.sa.script.Script):
    name = "HP.1905.get_interfaces"
    implements = [IGetInterfaces]

    rx_admin_status = re.compile(r"Port No\s+:(?P<interface>\d+).\s*"
                                "Active\s+:(?P<admin>(Yes|No)).*$",
                                re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ipif = re.compile(r"^\s+IP\[(?P<ip>\d+\.\d+\.\d+\.\d+)\],\s+"
                         "Netmask\[(?P<mask>\d+\.\d+\.\d+\.\d+)\],"
                         "\s+VID\[(?P<vid>\d+)\]$", re.MULTILINE)

    def execute(self):
        interfaces = []
        # Get portchannes
        portchannel_members = {}  # member -> (portchannel, type)
        """
        with self.cached():
            for pc in self.scripts.get_portchannel():
                i = pc["interface"]
                t = pc["type"] == "L"
                for m in pc["members"]:
                    portchannel_members[m] = (i, t)
        """
        if self.snmp and self.access_profile.snmp_ro:
            try:
                admin_status = {}
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.7", bulk=True):  # IF-MIB
                    if n[:3] == 'Aux' or n[:4] == 'Vlan' \
                    or n[:11] == 'InLoopBack':
                        continue
                    else:
                        admin_status.update({n: int(s) == 1})
            except self.snmp.TimeOutError:
                pass

        # Get mac
#        mac = self.scripts.get_chassis_id()
        # Get switchports
        for swp in self.scripts.get_switchport():
            admin = admin_status[swp["interface"]]
            name = swp["interface"]
            iface = {
                "name": name,
                "type": "aggregated" if len(swp["members"]) > 0 \
                else "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
#                "mac": mac,
                "subinterfaces": [{
                    "name": name,
                    "admin_status": admin,
                    "oper_status": swp["status"],
                    "enabled_afi": ['BRIDGE'],
#                    "mac": mac,
                    #"snmp_ifindex": self.scripts.get_ifindex(interface=name)
                }]
            }
            if swp["tagged"]:
                iface["subinterfaces"][0]["tagged_vlans"] = swp["tagged"]
            try:
                iface["subinterfaces"][0]["untagged_vlan"] = swp["untagged"]
            except KeyError:
                pass
            if swp["description"]:
                iface["description"] = swp["description"]
            if name in portchannel_members:
                iface["aggregated_interface"] = portchannel_members[name][0]
                if portchannel_members[name][1]:
                    n["enabled_protocols"] = ["LACP"]
            interfaces += [iface]

        return [{"interfaces": interfaces}]
