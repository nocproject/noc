# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.text import parse_table


class Script(NOCScript):
    """
    Cisco.SMB.get_interfaces
    """
    name = "Cisco.SMB.get_interfaces"
    implements = [IGetInterfaces]

    inttypes = {
           "Et": "physical",    # Ethernet
           "Fa": "physical",    # FastEthernet
           "Gi": "physical",    # GigabitEthernet
           "Lo": "loopback",    # Loopback
           "Po": "aggregated",  # Port-channel/Portgroup
           "Tu": "tunnel",      # Tunnel
           "Vl": "SVI",         # Vlan
           }

    def execute(self):

        reply = [{"forwarding_instance": "default",
            "type": "ip",
            "interfaces": [],}]

        interfaces = []
        # IPv4 interfaces:
        show_ip_int = self.cli("show ip int")
        for row in parse_table(show_ip_int):
            ipv4 = row[0].strip()
            try:
                iface = self.profile.convert_interface_name(row[1].strip())
            except:
                # skip gateway activity status for switch-mode
                continue
            for key in self.inttypes.keys():
                if re.match(key,iface,re.IGNORECASE):
                    inttype = self.inttypes[key]
                    break
            status = row[2].strip()
            try:
                admin_status = status.split("/")[0].lower() == 'up'
                oper_status  = status.split("/")[1].lower() == 'up'
            except:
                # just blind guess for some models like sf300
                # that haven't command to show vlan interface status
                admin_status = True
                oper_status = True
            interface = {
                "name": iface,
                "type": inttype,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": iface,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ipv4],
                    }],
                }
            interfaces.append(interface)

        # TODO: ipv6 interfaces

        # Physical interfaces:
        phys_int = []
        show_int_status = self.cli("show interfaces status")
        for row in parse_table(show_int_status):
            try:
                iface = self.profile.convert_interface_name(row[0].strip())
            except:
                # skip header for Port-Channel section
                continue
            for key in self.inttypes.keys():
                if re.match(key,iface,re.IGNORECASE):
                    inttype = self.inttypes[key]
                    break
            oper_status = row[6].strip().lower() == 'up'
            interface = {
                "name": iface,
                "type": inttype,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": iface,
                    "oper_status": oper_status,
                    "enabled_afi": ["BRIDGE"],
                }],
            }
            phys_int.append(interface)

        # refine admin status:
        show_int_conf = self.cli("show interfaces configuration",list_re=re.compile(r"^(?P<name>\S+)\s+(?P<type>\S+)\s+((?P<duplex>\S+)\s+)?(?P<speed>\S+)\s+(?P<neg>\S+)\s+(?P<flow>\S+)\s+(?P<admin_state>(up|down))\s*((?P<back_pressure>\S+)\s+(?P<mdix_mode>\S+)\s*)?$",re.IGNORECASE))
        for interface in show_int_conf:
            iface = self.profile.convert_interface_name(interface["name"])
            for key in phys_int:
                index = phys_int.index(key)
                if phys_int[index]["name"] == iface:
                    admin_status = interface["admin_state"].lower() == 'up'
                    phys_int[index]["admin_status"] = admin_status
                    phys_int[index]["subinterfaces"][0]["admin_status"] = admin_status

        # refine vlans:
        for sp in self.scripts.get_switchport():
            for key in phys_int:
                index = phys_int.index(key)
                if phys_int[index]["name"] == sp["interface"]:
                    phys_int[index]["subinterfaces"][0]["untagged_vlan"] = sp["untagged"]
                    phys_int[index]["subinterfaces"][0]["tagged_vlans"] = sp["tagged"]
                    if sp.has_key("description"):
                        phys_int[index]["description"] = sp["description"]
                        phys_int[index]["subinterfaces"][0]["description"] = sp["description"]

        # add missing interfaces:
        for interface in phys_int:
            found = False
            for i in interfaces:
                if i["name"] == interface["name"]:
                    found = True # already exists
            if not found:
                interfaces.append(interface)

        reply[0]["interfaces"] = interfaces
        return reply
