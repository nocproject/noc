# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
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

    rx_admin_status = re.compile(r"Port No\s+:(?P<interface>\d+).\s*"
                                "Active\s+:(?P<admin>(Yes|No)).*$",
                                re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ospf_status = re.compile(r"^\s+Internet Address (?P<ifaddr>"
                                "\d+\.\d+\.\d+\.\d+\/\d+).+$",
                                re.MULTILINE)
    rx_rip_status = re.compile(r"^\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
                               "(?P<mask>\d+\.\d+\.\d+\.\d+)\s+"
                               "(?P<direction>\S+)\s+.+$",
                               re.MULTILINE)
    rx_ipif = re.compile(r"^\s+IP\[(?P<ip>\d+\.\d+\.\d+\.\d+)\],\s+"
                         "Netmask\[(?P<mask>\d+\.\d+\.\d+\.\d+)\],"
                         "\s+VID\[(?P<vid>\d+)\]$", re.MULTILINE)

    def get_admin_status(self, iface):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # IF-MIB::ifAdminStatus
                s = self.snmp.get("1.3.6.1.2.1.2.2.1.7.%d" % int(iface))
                return int(s) == 1
            except self.snmp.TimeOutError:
                pass  # Fallback to CLI

        v = self.cli("show interface config %s" % iface)
        match = self.rx_admin_status.search(v)
        return match.group("admin").lower() == "yes"

    def get_ospf_addresses(self):
        """
        Returns set of IP addresses of OSPF interfaces
        :return: set of ip addresses
        :rtype: set
        """
        try:
            v = self.cli("show ip ospf interface", cached=True)
        except self.CLISyntaxError:
            return set()
        return set(match.group("ifaddr") for
            match in self.rx_ospf_status.finditer(v))

    def get_rip_addresses(self):
        """
        Returns set of IP addresses of RIP interfaces
        :return: set of ip addresses
        :rtype: set
        """
        try:
            v = self.cli("show router rip", cached=True)
        except self.CLISyntaxError:
            return set()
        return set(IPv4(match.group("ip"), netmask=match.group("mask")).prefix
            for match in self.rx_rip_status.finditer(v)
            if match.group("direction").lower() != "none")

    def execute(self):
        interfaces = []
        ospf_addresses = self.get_ospf_addresses()
        rip_addresses = self.get_rip_addresses()
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
        for match in self.rx_ipif.finditer(self.cli("show ip")):
            vid = int(match.group("vid"))
            ip = IPv4(match.group("ip"), netmask=match.group("mask")).prefix
            iface = {
                "name": "vlan%d" % vid if vid else "Mgmt",
                "type": "SVI",
                # since inactive vlans aren't shown at all
                "admin_status": True,
                "oper_status": True,
                "mac": mac,  # @todo get mgmt mac
                # @todo get vlan name
                "description": "vlan%d" % vid if vid else "Outband management",
                "subinterfaces": [{
                    "name": "vlan%d" % vid if vid else "Mgmt",
                    "admin_status": True,
                    "oper_status": True,
                    "is_ipv4": True,
                    "ipv4_addresses": [ip],  # @todo search for secondary IPs
                    "vlan_ids": [vid] if vid else []
                }]
            }
            if ip in rip_addresses:
                iface["subinterfaces"][0]["is_rip"] = True
            if ip in ospf_addresses:
                iface["subinterfaces"][0]["is_ospf"] = True
            interfaces += [iface]
        return [{"interfaces": interfaces}]
