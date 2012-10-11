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
        r"(GigabitEthernet|TenGigabitEthernet)", re.MULTILINE)
    rx_line_vlan = re.compile(r"\w*==========================\s+VLAN",
        re.MULTILINE)
    rx_name = re.compile(r"(?P<name>.+) is (?P<status>.\S+)\s+,", re.MULTILINE)
    rx_descr = re.compile(
        r"\s+interface's description:(\"\"|\"(?P<description>.+)\")",
        re.MULTILINE)
    rx_mac_local = re.compile(r"Hardware is  VLAN, address is (?P<mac>.\S+)",
        re.MULTILINE | re.IGNORECASE)
    rx_line_ip = re.compile(r"\n", re.MULTILINE | re.IGNORECASE)
    rx_ip_iface = re.compile(r"(?P<vlan_name>.+)",
        re.MULTILINE | re.IGNORECASE)
    rx_vlan = re.compile(r"VLAN\s+(?P<vlan>\d+)", re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(r"Interface address is:\s+(?P<ip>.+)",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
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
        # For each interface
        i = {
            "forwarding_instance": "default",
            "interfaces": [],
            "type": "physical"
        }
        for s in self.rx_line.split(v)[1:]:
            n = {}
            match = self.rx_name.search(s)
            if not match:
                continue
            iface = match.group("name")
            iface = self.profile.convert_interface_name(iface)
            status = match.group("status")

            match = self.rx_descr.search(s)
            description = match.group("description")

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
                            "is_bridge": True,
                        }]
            if switchports[iface][1]:
                n["subinterfaces"][0]["tagged_vlans"] = switchports[iface][1]
            if switchports[iface][0]:
                n["subinterfaces"][0]["untagged_vlan"] = switchports[iface][0]
            n["type"] = "physical"
            r += [n]
        for s in self.rx_line_vlan.split(v)[1:]:
            n = {}
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

            description = iface

            iface = {
                    "name": iface,
                    "type": "SVI",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": mac,
                    "description": description,
                    "subinterfaces": [{
                            "name": iface,
                            "description": description,
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": ["IPv4"],
                            "is_ipv4": True,
                            "ipv4_addresses": ip_list,
                            "mac": mac,
                            "vlan_ids": vlan_ids,
                            }]
                    }
            r += [iface]
        return [{"interfaces": r}]
