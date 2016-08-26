# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.ip import IPv4
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_interfaces"
    interface = IGetInterfaces

    rx_admin_status = re.compile(
        r"Port No\s+:(?P<interface>\d+).\s*"
        r"Active\s+:(?P<admin>(Yes|No)).*$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ospf_status = re.compile(
        r"^\s+Internet Address (?P<ifaddr>"
        r"\d+\.\d+\.\d+\.\d+\/\d+).+$",
        re.MULTILINE)
    rx_rip_status = re.compile(
        r"^\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<mask>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<direction>\S+)\s+.+$",
        re.MULTILINE)
    rx_ipif = re.compile(
        r"^\s+IP\[(?P<ip>\d+\.\d+\.\d+\.\d+)\],\s+"
        r"Netmask\[(?P<mask>\d+\.\d+\.\d+\.\d+)\],"
        r"\s+VID\[(?P<vid>\d+)\]$", re.MULTILINE)
    rx_ctp = re.compile(
        r"^\s+(?P<interface>\d+)\s+\S+"
        r"\s+(?P<state>\S+)\s+\d+"
        r"\s+\d+\s+\d+\s+.+$",
        re.MULTILINE)
    rx_gvrp = re.compile(
        r"^Port\s+(?P<interface>\d+)$",
        re.MULTILINE)

    # @todo: vlan trunking, STP, LLDP (fw >= 3.90)

    def get_admin_status(self, iface):
        """
        Returns admin status of the interface
        """
        if self.has_snmp():
            try:
                # IF-MIB::ifAdminStatus
                s = self.snmp.get(mib["IF-MIB::ifAdminStatus", int(iface)])
                return int(s) == 1
            except self.snmp.TimeOutError:
                pass  # Fallback to CLI

        s = self.cli("show interface config %s" % iface)
        match = self.rx_admin_status.search(s)
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

        # Get ifindexes
        ifindexes = self.scripts.get_ifindexes()

        # Get portchannes
        portchannel_members = {}  # member -> (portchannel, type)
        with self.cached():
            for pc in self.scripts.get_portchannel():
                i = pc["interface"]
                t = pc["type"] == "L"
                for m in pc["members"]:
                    portchannel_members[m] = (i, t)
        # Get portchannel members' details
        for m in portchannel_members:
            admin = self.get_admin_status(m)
            oper = self.scripts.get_interface_status(interface=m)[0]["status"]
            iface = {
                "name": m,
                "admin_status": admin,
                "oper_status": oper,
                "type": "physical",
                "subinterfaces": [],
                "aggregated_interface": portchannel_members[m][0],
                # @todo: description
            }
            if portchannel_members[m][1]:
                iface["enabled_protocols"] = ["LACP"]
            interfaces += [iface]

        # Get loopguard
        ctp = {}
        try:
            cmd = self.cli("show loopguard")
            if "LoopGuard Status: Enable" in cmd:
                for match in self.rx_ctp.finditer(cmd):
                    ctp[match.group("interface")] = match.group("state")
        except self.CLISyntaxError:
            pass

        # Get gvrp
        gvrp = []
        cmd = self.cli("show vlan1q gvrp")
        if "gvrpEnable = YES" in cmd:
            for match in self.rx_gvrp.finditer(cmd):
                gvrp += [match.group("interface")]

        # Get mac
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]

        # Get switchports
        for swp in self.scripts.get_switchport():
            admin = False
            if len(swp["members"]) > 0:
                for m in swp["members"]:
                    admin = self.get_admin_status(m)
                    if admin:
                        break
            else:
                admin = self.get_admin_status(swp["interface"])
            name = swp["interface"]
            iface = {
                "name": name,
                "type": "aggregated" if len(swp["members"]) > 0
                    else "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
                "mac": mac,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": name,
                    "admin_status": admin,
                    "oper_status": swp["status"],
                    "enabled_afi": ["BRIDGE"],
                    "mac": mac,
                    "snmp_ifindex": ifindexes.get(name)
                }]
            }
            iface["snmp_ifindex"] = iface["subinterfaces"][0]["snmp_ifindex"]
            if swp["tagged"]:
                iface["subinterfaces"][0]["tagged_vlans"] = swp["tagged"]
            try:
                iface["subinterfaces"][0]["untagged_vlan"] = swp["untagged"]
            except KeyError:
                pass
            if "description" in swp.keys():
                iface["description"] = swp["description"]
                iface["subinterfaces"][0]["description"] = swp["description"]
            if len(ctp) > 0:
                if ctp[name] == "Enable":
                    iface["enabled_protocols"] += ["CTP"]
            if name in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            interfaces += [iface]

        # Get SVIs
        ipifarr = {}
        for match in self.rx_ipif.finditer(self.cli("show ip")):
            vid = int(match.group("vid"))
            ip = IPv4(match.group("ip"), netmask=match.group("mask")).prefix
            if vid not in ipifarr:
                ipifarr[vid] = [ip]
            else:
                ipifarr[vid].append(ip)
        for v in ipifarr.keys():
            iface = {
                "name": "vlan%d" % v if v else "Management",
                "mac": mac,  # @todo: get mgmt mac
                # @todo: get vlan name to form better description
                "description": "vlan%d" % v if v else "Outband management",
                "admin_status": True,  # always True, since inactive
                "oper_status": True,   # SVIs aren't shown at all
                "subinterfaces": [{
                    "name": "vlan%d" % v if v else "Management",
                    "description": "vlan%d" % v if v else "Outband management",
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": ipifarr[v],
                    "mac": mac,
                    "enabled_protocols": []
                }]
            }
            if v == 0:  # Outband management
                iface["type"] = "management"
                # @todo: really get status
            else:
                iface["type"] = "SVI"
                iface["subinterfaces"][0]["vlan_ids"] = [v]
            for i in ipifarr[v]:
                if i in rip_addresses:
                    iface["subinterfaces"][0]["enabled_protocols"] += ["RIP"]
                if i in ospf_addresses:
                    iface["subinterfaces"][0]["enabled_protocols"] += ["OSPF"]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
