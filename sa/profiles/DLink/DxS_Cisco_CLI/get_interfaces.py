# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces, InterfaceTypeError


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_interfaces"
    implements = [IGetInterfaces]

    rx_line = re.compile(
        r"\w*==========================\s+"
        r"(GigabitEthernet|TenGigabitEthernet|AggregatePort)", re.MULTILINE)
    rx_line_vlan = re.compile(r"\w*==========================\s+VLAN",
                              re.MULTILINE)
    rx_ifindex = re.compile(r"Index\(dec\):(?P<ifindex>\d+) \(hex\):\d+")
    rx_name = re.compile(r"^(?P<name>\S+.+) is (?P<status>.\S+)(|\s+),",
                         re.MULTILINE)
    rx_descr = re.compile(
        r"\s+interface's description:(\"\"|\"(?P<description>.+)\")",
        re.MULTILINE)
    rx_mac_local = re.compile(r"Hardware is  VLAN, address is (?P<mac>.\S+)",
                              re.MULTILINE | re.IGNORECASE)
    rx_line_ip = re.compile(r"\n", re.MULTILINE | re.IGNORECASE)
    rx_ip_iface = re.compile(r"(?P<vlan_name>.+)",
                             re.MULTILINE | re.IGNORECASE)
    rx_vlan = re.compile(r"VLAN\s+(?P<vlan>\d+)", re.MULTILINE | re.IGNORECASE)
    rx_des = re.compile(r"Description:\s+(?P<des>.+)",
                       re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(r"Interface address is:\s+(?P<ip>.+)",
                       re.MULTILINE | re.IGNORECASE)
    rx_ospf_gs = re.compile(r"Routing Protocol is \"ospf \d+\"")
    rx_ospf = re.compile(r"^(?P<if_ospf>.+)\s+is up, line protocol is up",
                         re.IGNORECASE)
    rx_lldp_gs = re.compile(r"Global\s+status\s+of\s+LLDP\s+:\s+Enable")
    rx_lldp = re.compile(r"Port\s+\[(?P<port>.+)\]\nPort status of LLDP\s+:\s+Enable",
                         re.IGNORECASE)
    types = {
        "Gi": "physical",    # GigabitEthernet
        "Lo": "loopback",    # Loopback
        "Ag": "aggregated",  # Port-channel/Portgroup
        "Te": "physical",    # TenGigabitEthernet
        "VL": "SVI",         # VLAN, found on C3500XL
        "Vl": "SVI"
    }

    def execute(self):
        try:
            c_proto = self.cli("show ip protocols")
        except self.CLISyntaxError:
            c_proto = ""
        lldp = []
        try:
            c = self.cli("show lldp status | include Global")
        except self.CLISyntaxError:
            c = ""
        lldp_enable = self.rx_lldp_gs.search(c) is not None
        if lldp_enable:
            try:
                c = self.cli("show lldp status | include Port")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_lldp.finditer(c):
                port = match.group("port")
                iface_lldp = self.profile.convert_interface_name(port)
                lldp += [iface_lldp]

        ospf = []
        ospf_enable = self.rx_ospf_gs.search(c_proto) is not None
        if ospf_enable:
            try:
                c = self.cli("show ip ospf interface")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_ospf.finditer(c):
                if_ospf = match.group("if_ospf")
                iface_ospf = self.profile.convert_interface_name(if_ospf)
                ospf += [if_ospf]

        r = []
        try:
            v = self.cli("show interfaces")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        switchports = {}  # interface -> (untagged, tagged)
        for swp in self.scripts.get_switchport():
            switchports[swp["interface"]] = (
                swp["untagged"] if "untagged" in swp else None,
                swp["tagged"]
            )
        v = "\n" + v
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        i = {
            "forwarding_instance": "default",
            "interfaces": [],
            "type": "physical"
        }
            # Portchanel
        for s in self.rx_line.split(v)[1:]:
            n = {}
            enabled_protocols = []
            ifindex = 0
            match = self.rx_ifindex.search(s)
            if match:
                ifindex = int(match.group("ifindex"))
            match = self.rx_name.search(s)
            if not match:
                continue
            iface = match.group("name")
            iface = self.profile.convert_interface_name(iface)
            status = match.group("status")

            match = self.rx_descr.search(s)
            description = match.group("description")
            if description:
                description = description.decode("ascii","ignore")
            if iface in portchannel_members:
                ai, is_lacp = portchannel_members[iface]
                n["aggregated_interface"] = ai
                n["enabled_protocols"] = ["LACP"]
            n["name"] = iface
            n["admin_status"] = True
            n["oper_status"] = status
            n["description"] = description
            n["subinterfaces"] = [{
                "name": iface,
                "description": description,
                "admin_status": True,
                "oper_status": status,
                "enabled_afi": ["BRIDGE"],
            }]
            if ifindex != 0:
                n["snmp_ifindex"] = ifindex
            if lldp_enable and iface in lldp:
                enabled_protocols += ["LLDP"]
            n["enabled_protocols"] = enabled_protocols

            if iface in switchports:
                if switchports[iface][1]:
                    n["subinterfaces"][0]["tagged_vlans"] = switchports[iface][1]
                if switchports[iface][0]:
                    n["subinterfaces"][0]["untagged_vlan"] = switchports[iface][0]
            n["type"] = self.types[iface[:2]]
            r += [n]
        for s in self.rx_line_vlan.split(v)[1:]:
            n = {}
            ifindex = 0
            description = None
            match = self.rx_ifindex.search(s)
            if match:
                ifindex = int(match.group("ifindex"))
            match = self.rx_name.search(s)
            if not match:
                continue
            iface = match.group("name")
            status = match.group("status")
            match = self.rx_ip.search(s)
            ip = match.group("ip")
            if ip == "no ip address":
                ip = "127.0.0.1/32"
            match = self.rx_vlan.search(s)
            vlan = match.group("vlan")
            vlan_ids = [vlan]
            ip_list = [ip]
            match = self.rx_mac_local.search(s)
            mac = match.group("mac")
            match = self.rx_des.search(s)
            if match:
                description = match.group("des").decode("ascii","ignore")

            enabled_protocols = []
            if ospf_enable and iface in ospf:
                enabled_protocols += ["OSPF"]

            iface = {"name": iface,
                     "type": "SVI",
                     "admin_status": True,
                     "oper_status": True,
                     "mac": mac,
                     "subinterfaces": [{
                             "name": iface,
                             "admin_status": True,
                             "oper_status": True,
                             "enabled_afi": ["IPv4"],
                             "ipv4_addresses": ip_list,
                             "mac": mac,
                             "enabled_protocols": enabled_protocols,
                             "vlan_ids": vlan_ids,
                     }]}
            if ifindex != 0:
                iface["snmp_ifindex"] = ifindex
            if description:
                iface["description"] = description
                iface["subinterfaces"][0]["description"] = description
            r += [iface]
        return [{"interfaces": r}]
