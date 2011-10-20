# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
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
    name = "Zyxel.ZyNOS.get_interfaces"
    implements = [IGetInterfaces]

    def get_admin_status(self, iface):
        rx_admin_status = re.compile(r"Port No\s+:(?P<interface>\d+).\s*Active" \
                                    "\s+:(?P<admin>(Yes|No)).*$",
                                    re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if self.snmp and self.access_profile.snmp_ro:
            try:
                s = self.snmp.get("1.3.6.1.2.1.2.2.1.7.%d" % int(iface))  # IF-MIB::ifAdminStatus
                return int(s) == 1
            except self.snmp.TimeOutError:
                pass  # Fallback to CLI

        match = rx_admin_status.search(self.cli("show interface config %s" % iface))
        return True if match.group("admin").lower() == "yes" else False

    def is_ospf(self, ifaddr):
        rx_ospf_status = re.compile(r"^\s+Internet Address (?P<ifaddr>" \
                                    "\d+\.\d+\.\d+\.\d+\/\d+).+$",
                                    re.MULTILINE)
        try:
            for match in rx_ospf_status.finditer(self.cli("show ip ospf interface", cached=True)):
                if match.group("ifaddr") == ifaddr:
                    return True
        except self.CLISyntaxError:
            pass
        return False

    def is_rip(self, ifaddr):
        rx_rip_status = re.compile(r"^\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+" \
                                    "(?P<mask>\d+\.\d+\.\d+\.\d+)\s+" \
                                    "(?P<direction>\S+)\s+.+$",
                                    re.MULTILINE)
        try:
            for match in rx_rip_status.finditer(self.cli("show router rip", cached=True)):
                if ifaddr == IPv4(match.group("ip"), netmask=match.group("mask")).prefix and match.group("direction") != "None":
                    return True
        except self.CLISyntaxError:
            pass
        return False

    def execute(self):
        interfaces = []

        # Get portchannes
        portchannel_members = {}  # member -> (portchannel, type)
        with self.cached():
            for pc in self.scripts.get_portchannel():
                i = pc["interface"]
                t = pc["type"] == "L"
                for m in pc["members"]:
                    portchannel_members[m] = (i, t)

        # Get mac
        mac = self.scripts.get_chassis_id()

        # Get switchports
        for swp in self.scripts.get_switchport():
            admin = self.get_admin_status(swp["interface"])
            name = swp["interface"]
            iface = {
                "name": name,
                "type": "aggregated" if len(swp["members"]) > 0 else "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
                "mac": mac,
                "subinterfaces": [{
                    "name": name,
                    "admin_status": admin,
                    "oper_status": swp["status"],
                    "is_bridge": True,
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
                iface["is_lacp"] = portchannel_members[name][1]
            interfaces += [iface]

        # Get SVIs
        rx_ipif = re.compile(r"^\s+IP\[(?P<ip>\d+\.\d+\.\d+\.\d+)\],\s+Netmask" \
                                "\[(?P<mask>\d+\.\d+\.\d+\.\d+)\],\s+VID" \
                                "\[(?P<vid>\d+)\]$", re.MULTILINE)
        for match in rx_ipif.finditer(self.cli("show ip")):
            vid = int(match.group("vid"))
            ip = IPv4(match.group("ip"), netmask=match.group("mask")).prefix
            iface = {
                "name": "vlan%d" % vid if vid else "Mgmt",
                "type": "SVI",
                "admin_status": True,  # since inactive vlans aren't shown at all
                "oper_status": True,
                "mac": mac,  # @todo get mgmt mac
                "description": "vlan%d" % vid if vid else "Outband management",  # @todo get vlan name
                "subinterfaces": [{
                    "name": "vlan%d" % vid if vid else "Mgmt",
                    "admin_status": True,
                    "oper_status": True,
                    "is_ipv4": True,
                    "ipv4_adresses": [ip],  # @todo search for secondary IPs
                    "vlan_ids": [vid] if vid else []
                }]
            }
            if self.is_rip(ip):
                iface["subinterfaces"][0]["is_rip"] = True
            if self.is_ospf(ip):
                iface["subinterfaces"][0]["is_ospf"] = True
            interfaces += [iface]

        return [{"interfaces": interfaces}]
