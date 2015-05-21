# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    name = "Supertel.K2X.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 240

    rx_sh_ip_int = re.compile(
        r"^(?P<ip>\S+)/(?P<mask>\d+)\s+(?P<interface>(\S+ \d+|\S+))\s+"
        r"(Static|DHCP)\s*$",
        re.MULTILINE)

    rx_sh_ipv6_int = re.compile(
        r"^(?P<interface>(\S+ \d+|\S+))\s+(?P<ip>\S+)(/(?P<mask>\d+)|)\s+"
        r"(manual|linklayer|Static|Dynamic)\s*$",
        re.MULTILINE)

    rx_status = re.compile(
        r"^(?P<interface>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+\s+|)"
        r"(?P<oper_status>(Up|Down|Down*))",
        re.MULTILINE)

    types = {
        "g": "physical",    # GigabitEthernet
        "c": "aggregated",  # Port-channel/Portgroup
        "V": "SVI",         # Vlan interface
        "v": "SVI",         # Vlan interface
        }

    def execute(self):
        # Get port-to-vlan mappings
        pvm = {}
        switchports = {}  # interface -> (untagged, tagged)
        for sp in self.scripts.get_switchport():
            switchports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"]
                )

        # Get IP interfaces
        mac = self.scripts.get_chassis_id()
        mac = mac[0]['first_chassis_mac']
        interfaces = []
        ip_iface = self.cli("show ip interface")
        for match in self.rx_sh_ip_int.finditer(ip_iface):
            ifname = match.group("interface")
            typ = self.types[ifname[:1]]
            ip = match.group("ip")
            netmask = match.group("mask")
            ip = ip + '/' + netmask
            a_stat = True
            o_stat = True
            iface = {
                "name": ifname,
                "type": typ,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "mac": mac,
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip],
                    "mac": mac,
                    }]
                }
            interfaces += [iface]

        ip_iface = self.cli("show ipv6 interface")
        for match in self.rx_sh_ipv6_int.finditer(ip_iface):
            ifname = match.group("interface")
            ip = match.group("ip")

            if match.group("mask"):
                netmask = match.group("mask")
                ip = ip + '/' + netmask
            elif '/' not in ip:
                netmask = "64"
                ip = ip + '/' + netmask

            ifac = True
            for i in interfaces:
                if i["name"] == ifname:
                    ifac = False
                    i["subinterfaces"][0]["ipv6_addresses"] += [ip]
                    if "IPv6" not in i["subinterfaces"][0]["enabled_afi"]:
                        i["subinterfaces"][0]["enabled_afi"] += ["IPv6"]

            if ifac:
                typ = self.types[ifname[:1]]
                a_stat = True
                o_stat = True
                iface = {
                    "name": ifname,
                    "type": typ,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "mac": mac,
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "enabled_afi": ["IPv6"],
                        "ipv6_addresses": [ip],
                        "mac": mac,
                        }]
                    }
                interfaces += [iface]

        status = self.cli("show interfaces status")
        config = self.cli("show interfaces configuration")
        descr = self.cli("show interfaces description")
        gvrp = self.cli("show gvrp configuration")
        lldp = self.cli("show lldp configuration")
        stp = self.cli("show spanning-tree")

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        for match in self.rx_status.finditer(status):
            ifname = match.group("interface")
            o_stat = match.group("oper_status").lower() == "up"
            if ifname[:1] == 'g':
                ifindex = ifname[1:]
                rx_config = re.compile(
                    r"^" + ifname + "\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
                    r"(?P<admin_status>(Up|Down))\s+\S+\s+\S+$",
                    re.MULTILINE)
            else:
                ifindex = str(999 + int(ifname[2:]))
                rx_config = re.compile(
                    r"^" + ifname + "\s+\S+\s+\S+\s+\S+\s+\S+\s+"
                    r"(?P<admin_status>(Up|Down))\s*$",
                    re.MULTILINE)
            match = rx_config.search(config)
            a_stat = match.group("admin_status").lower() == "up"
            rx_descr = re.compile(
                r"^" + ifname + "\s+(?P<desc>\S+)$", re.MULTILINE)
            match = rx_descr.search(descr)
            if match:
                description = match.group("desc")
            else:
                description = ''

            ifac = True
            for i in interfaces:
                if i["name"] == ifname:
                    ifac = False
                    i["admin_status"] = a_stat
                    i["oper_status"] = o_stat
                    i["description"] = description
                    i["enabled_protocols"] = []
                    i["subinterfaces"][0]["admin_status"] = a_stat
                    i["subinterfaces"][0]["oper_status"] = o_stat
                    i["subinterfaces"][0]["description"] = description
                    i["subinterfaces"][0]["snmp_ifindex"] = ifindex
                    iface = i

            if ifac:
                iface = {
                    "name": ifname,
                    "type": self.types[ifname[:1]],
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "mac": mac,
                    "description": description,
                    "enabled_protocols": [],
                    "snmp_ifindex": ifindex,
                    "subinterfaces": [{
                        "name": ifname,
                        "description": description,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "mac": mac,
                        "enabled_afi": [],
                        "snmp_ifindex": ifindex
                        }]
                    }
                interfaces += [iface]

            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            elif ifac:
                iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
                if switchports[ifname][1]:
                    iface["subinterfaces"][0]["tagged_vlans"] = switchports[
                        ifname][1]
                if switchports[ifname][0]:
                    iface["subinterfaces"][0]["untagged_vlan"] = switchports[
                        ifname][0]

            # GVRP
            rx_gvrp = re.compile(
                r"^" + ifname + "\s+Enabled\s+Normal\s+"
                r"Enabled\s+\d+\s+\d+\s+\d+",
                re.MULTILINE)
            match = rx_gvrp.search(gvrp)
            if match:
                iface["enabled_protocols"] += ["GVRP"]

            # LLDP
            rx_lldp = re.compile(
                r"^" + ifname + "\s+(Rx and Tx|Rx|Tx)\s+", re.MULTILINE)
            match = rx_lldp.search(lldp)
            if match:
                iface["enabled_protocols"] += ["LLDP"]

            # STP
            rx_stp = re.compile(
                r"^\s*" + ifname + "\s+enabled\s+\S+\s+\d+\s+"
                r"\S+\s+\S+\s+(Yes|No)\s+", re.MULTILINE)
            match = rx_stp.search(stp)
            if match:
                iface["enabled_protocols"] += ["STP"]

        return [{"interfaces": interfaces}]
