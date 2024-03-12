# ---------------------------------------------------------------------
# CData.xPON.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.text import split_alnum


class Script(BaseScript):
    name = "CData.xPON.get_interfaces"
    interface = IGetInterfaces

    rx_vlan = re.compile(
        r"^\s*Vlan-ID: (?P<vlan_id>\d+)\s+Vlan-Name: (?P<vlan_name>.+)\n"
        r"(^\s*User-bridge: .+\n)?"
        r"^\s*Untagged-Ports:(?P<untagged>.+)\n"
        r"^\s*Tagged-Ports:(?P<tagged>.+)\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_port = re.compile(
        r"ifIndex:\s+(?P<snmp_ifindex>\d+), linkStatus: (?P<oper_status>\d+), "
        r"portName:\s+(?P<ifname>\S+),"
    )
    rx_agg = re.compile(
        r"^\s*(?P<num>\d+)\s+(?P<type>Lacp|Manual)\s+(?P<ifaces>[xg]\S+\d), ", re.MULTILINE
    )
    rx_mgmt = re.compile(
        r"^Status : (?P<oper_status>\S+)\s*\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"^Internet Address is (?P<ip>\S+), netmask (?P<mask>\S+)\s*\n"
        r"^Hardware address is (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_mgmt2 = re.compile(
        r"^\s*(?P<ifname>\S+) current state: (?P<admin_status>\S+)\s*\n"
        r"^\s*Line protocol current state: (?P<oper_status>\S+)\s*\n"
        r"^\s*Description: (?P<descr>.+)\n"
        r"^\s*Internet Address is (?P<ip_address>\S+)\s*\n"
        r"^\s*The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"^\s*IP Sending Frames.*\n"
        r"^\s*Hardware Address is (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlanif = re.compile(
        r"^Description : Inband interface (?P<ifname>vlanif\d+) is (?P<oper_status>\S+), "
        r"administrator status is (?P<admin_status>\S+)\s*\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"^Internet Address is (?P<ip>\S+), netmask (?P<mask>\S+)\s*\n"
        r"^Hardware address is (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlanif2 = re.compile(
        r"^\s*(?P<ifname>Vlanif\d+) current state: (?P<admin_status>\S+)\s*\n"
        r"^\s*Line protocol current state: (?P<oper_status>\S+)\s*\n"
        r"^\s*Description: (?P<descr>.+)\n"
        r"^\s*Internet Address is (?P<ip_address>\S+)\s*\n"
        r"^\s*The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"^\s*IP Sending Frames.*\n"
        r"^\s*Hardware Address is (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlanid = re.compile(r"[Vv]lanif(?P<vlan_id>\d+)")

    @staticmethod
    def iter_range(s):
        if "-" not in s:
            yield s
        else:
            first, last = s.rsplit("-", 1)
            parts = split_alnum(first)
            prefix = parts[:-1]
            last = last.rsplit("/", 1)[1]
            for i in range(int(parts[-1]), int(last) + 1):
                yield "".join([str(x) for x in prefix + [i]])

    def execute_cli(self, **kwargs):
        vlans = []
        interfaces = []
        with self.configure():
            v = self.cli("show vlan all")
            for vlan in v.split("-----\n"):
                match = self.rx_vlan.search(vlan)
                if match:
                    vlan_id = match.group("vlan_id")
                    tagged = match.group("tagged").split()
                    untagged = match.group("untagged").split()
                    vlans += [
                        {
                            "vlan_id": vlan_id,
                            "untagged": untagged,
                            "tagged": tagged,
                        }
                    ]
            v = self.cli("show lacp system port")
            for match in self.rx_port.finditer(v):
                ifname = match.group("ifname")
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": match.group("oper_status").lower() == "1",
                    "enabled_protocols": [],
                    "subinterfaces": [],
                }
                sub = {
                    "name": ifname,
                    "admin_status": True,
                    "oper_status": match.group("oper_status").lower() == "1",
                    "enabled_afi": ["BRIDGE"],
                    "enabled_protocols": [],
                }
                for vlan in vlans:
                    if ifname in vlan["untagged"]:
                        sub["untagged_vlan"] = vlan["vlan_id"]
                    if ifname in vlan["tagged"]:
                        if "tagged_vlans" in sub:
                            sub["tagged_vlans"] += [vlan["vlan_id"]]
                        else:
                            sub["tagged_vlans"] = [vlan["vlan_id"]]
                iface["subinterfaces"] += [sub]
                interfaces += [iface]
            v = self.cli("show link-aggregation group summary")
            for match in self.rx_agg.finditer(v):
                if match.group("type") == "Manual":
                    ifname = "lag" + match.group("num")
                else:
                    ifname = "lagL" + match.group("num")
                    iface = {
                        "name": ifname,
                        "type": "aggregated",
                        "admin_status": True,
                        "oper_status": True,
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "admin_status": True,
                                "oper_status": True,
                                "enabled_afi": ["BRIDGE"],
                            }
                        ],
                    }
                    interfaces += [iface]
                for vlan in vlans:
                    if (ifname not in vlan["untagged"]) and (ifname not in vlan["tagged"]):
                        continue
                    for phys_iface in self.iter_range(match.group("ifaces")):
                        for phys_ifaces in interfaces:
                            if phys_iface == phys_ifaces["name"]:
                                phys_ifaces["aggregated_interface"] = ifname
                                if "L" in ifname:
                                    phys_ifaces["protovols"] = ["LACP"]
                                sub = phys_ifaces["subinterfaces"][0]
                                if ifname in vlan["untagged"]:
                                    sub["untagged_vlan"] = vlan["vlan_id"]
                                if ifname in vlan["tagged"]:
                                    if "tagged_vlans" in sub:
                                        sub["tagged_vlans"] += [vlan["vlan_id"]]
                                    else:
                                        sub["tagged_vlans"] = [vlan["vlan_id"]]
            try:
                v = self.cli("show interface vlanif")
                for match in self.rx_vlanif.finditer(v):
                    ifname = match.group("ifname")
                    ip_address = match.group("ip")
                    ip_mask = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_mask))
                    vlan_id = self.rx_vlanid.search(ifname).group("vlan_id")
                    iface = {
                        "name": ifname,
                        "type": "SVI",
                        "admin_status": match.group("admin_status").lower() == "up",
                        "oper_status": match.group("oper_status").lower() == "up",
                        "mac": match.group("mac"),
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "admin_status": match.group("admin_status").lower() == "up",
                                "oper_status": match.group("oper_status").lower() == "up",
                                "mtu": match.group("mtu"),
                                "enabled_afi": ["IPv4"],
                                "ipv4_addresses": [ip_address],
                                "vlan_id": vlan_id,
                            }
                        ],
                    }
                    interfaces += [iface]
                for match in self.rx_vlanif2.finditer(v):
                    ifname = match.group("ifname")
                    vlan_id = self.rx_vlanid.search(ifname).group("vlan_id")
                    iface = {
                        "name": ifname,
                        "type": "SVI",
                        "admin_status": match.group("admin_status").lower() == "up",
                        "oper_status": match.group("oper_status").lower() == "up",
                        "mac": match.group("mac"),
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "admin_status": match.group("admin_status").lower() == "up",
                                "oper_status": match.group("oper_status").lower() == "up",
                                "mtu": match.group("mtu"),
                                "enabled_afi": ["IPv4"],
                                "ipv4_addresses": [match.group("ip_address")],
                                "vlan_id": vlan_id,
                            }
                        ],
                    }
                    interfaces += [iface]
            except self.CLISyntaxError:
                pass

            try:
                v = self.cli("show interface mgmt")
                match = self.rx_mgmt.search(v)
                if match:
                    ip_address = match.group("ip")
                    ip_mask = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_mask))
                    iface = {
                        "name": "mgmt",
                        "type": "management",
                        "admin_status": True,
                        "oper_status": match.group("oper_status").lower() == "enable",
                        "mac": match.group("mac"),
                        "subinterfaces": [
                            {
                                "name": "mgmt",
                                "admin_status": True,
                                "oper_status": match.group("oper_status").lower() == "enable",
                                "mtu": match.group("mtu"),
                                "enabled_afi": ["IPv4"],
                                "ipv4_addresses": [ip_address],
                            }
                        ],
                    }
                    interfaces += [iface]
                else:
                    match = self.rx_mgmt2.search(v)
                    if match:
                        iface = {
                            "name": match.group("ifname"),
                            "type": "management",
                            "admin_status": match.group("admin_status").lower() == "up",
                            "oper_status": match.group("oper_status").lower() == "up",
                            "mac": match.group("mac"),
                            "subinterfaces": [
                                {
                                    "name": match.group("ifname"),
                                    "admin_status": match.group("admin_status").lower() == "up",
                                    "oper_status": match.group("oper_status").lower() == "up",
                                    "mtu": match.group("mtu"),
                                    "enabled_afi": ["IPv4"],
                                    "ipv4_addresses": [match.group("ip_address")],
                                }
                            ],
                        }
                        interfaces += [iface]
            except self.CLISyntaxError:
                pass

        return [{"interfaces": interfaces}]
