# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


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
=======
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_interfaces"
    implements = [IGetInterfaces]

    rx_admin_status = re.compile(r"Port No\s+:(?P<interface>\d+).\s*"
                                r"Active\s+:(?P<admin>(Yes|No)).*$",
                                re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ospf_status = re.compile(r"^\s+Internet Address (?P<ifaddr>"
                                r"\d+\.\d+\.\d+\.\d+\/\d+).+$",
                                re.MULTILINE)
    rx_rip_status = re.compile(r"^\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
                               r"(?P<mask>\d+\.\d+\.\d+\.\d+)\s+"
                               r"(?P<direction>\S+)\s+.+$",
                               re.MULTILINE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_ipif = re.compile(
        r"^\s+IP\[(?P<ip>\d+\.\d+\.\d+\.\d+)\],\s+"
        r"Netmask\[(?P<mask>\d+\.\d+\.\d+\.\d+)\],"
        r"\s+VID\[(?P<vid>\d+)\]$", re.MULTILINE)
<<<<<<< HEAD
    rx_ctp = re.compile(
        r"^\s+(?P<interface>\d+)\s+\S+\s+Enable\s+\d+"
        r"\s+\d+\s+\d+\s+.+$",
        re.MULTILINE)
    rx_gvrp = re.compile(
        r"^Port\s+(?P<interface>\d+)$",
        re.MULTILINE)

    # @todo: vlan trunking, STP, LLDP (fw >= 3.90)
=======

    # @todo: vlan trunking, STP, CTP aka LBD
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def get_admin_status(self, iface):
        """
        Returns admin status of the interface
        """
<<<<<<< HEAD
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # IF-MIB::ifAdminStatus
                s = self.snmp.get("1.3.6.1.2.1.2.2.1.7.%d" % int(iface))
                return int(s) == 1
            except self.snmp.TimeOutError:
                pass  # Fallback to CLI

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        return set(
            match.group("ifaddr") for match in self.rx_ospf_status.finditer(v)
        )
=======
        return set(match.group("ifaddr") for
            match in self.rx_ospf_status.finditer(v))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
        return set(
            IPv4(match.group("ip"), netmask=match.group("mask")).prefix
            for match in self.rx_rip_status.finditer(v)
            if match.group("direction").lower() != "none"
        )
=======
        return set(IPv4(match.group("ip"), netmask=match.group("mask")).prefix
            for match in self.rx_rip_status.finditer(v)
            if match.group("direction").lower() != "none")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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

<<<<<<< HEAD
        # Get loopguard
        ctp = []
        try:
            cmd = self.cli("show loopguard")
            if "LoopGuard Status: Enable" in cmd:
                for match in self.rx_ctp.finditer(cmd):
                    ctp += [match.group("interface")]
        except self.CLISyntaxError:
            pass

        # Get gvrp
        gvrp = []
        cmd = self.cli("show vlan1q gvrp")
        if "gvrpEnable = YES" in cmd:
            for match in self.rx_gvrp.finditer(cmd):
                gvrp += [match.group("interface")]

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                "type": "aggregated" if len(swp["members"]) > 0 else "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
                "mac": mac,
                "enabled_protocols": [],
=======
                "type": "aggregated" if len(swp["members"]) > 0
                    else "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
                "mac": mac,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                "subinterfaces": [{
                    "name": name,
                    "admin_status": admin,
                    "oper_status": swp["status"],
                    "enabled_afi": ["BRIDGE"],
<<<<<<< HEAD
                    "mac": mac
=======
                    "mac": mac,
                    #"snmp_ifindex": self.scripts.get_ifindex(interface=name)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                }]
            }
            if swp["tagged"]:
                iface["subinterfaces"][0]["tagged_vlans"] = swp["tagged"]
            try:
                iface["subinterfaces"][0]["untagged_vlan"] = swp["untagged"]
            except KeyError:
                pass
<<<<<<< HEAD
            if "description" in swp.keys():
                iface["description"] = swp["description"]
                iface["subinterfaces"][0]["description"] = swp["description"]
            if name in ctp:
                iface["enabled_protocols"] += ["CTP"]
            if name in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
=======
            if swp["description"]:
                iface["description"] = swp["description"]
                iface["subinterfaces"][0]["description"] = swp["description"]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
