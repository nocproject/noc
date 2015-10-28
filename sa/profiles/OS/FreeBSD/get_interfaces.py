# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.ip import IPv4
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_interfaces"
    interface = IGetInterfaces
    rx_if_name = re.compile(
        r"^(?P<ifname>\S+): flags=[0-9a-f]+<(?P<flags>\S+)>( metric \d+)?"
        r" mtu (?P<mtu>\d+)$")
    rx_if_descr = re.compile(r"^\tdescription: (?P<descr>.+)\s*$")
    rx_if_mac = re.compile(r"^\tether (?P<mac>\S+)\s*$")
    rx_if_inet = re.compile(
        r"^\tinet (?P<inet>\S+) netmask (?P<netmask>\S+)\s*(broadcast .+)?$")
    rx_if_inet6 = re.compile(
    r"^\tinet6 (?P<inet6>\S+) prefixlen (?P<prefixlen>\S+)\s*(scopeid .+)?$")
    rx_if_status = re.compile(
        r"^\tstatus: (?P<status>active|associated|running|inserted)\s*$")
    rx_if_vlan = re.compile(
        r"^\tvlan: (?P<vlan>[1-9]\d*) parent interface: (?P<parent>\S+)$")
    rx_if_wlan = re.compile(r"^\tssid .+$")
    rx_if_bridge = re.compile(r"^\tgroups:.+?bridge.*?$")
    rx_if_bridge_m = re.compile(r"^\tmember: (?P<ifname>\S+) flags=\d+<.+>$")
    rx_if_bridge_s = re.compile(r"cost \d+ proto r?stp$")
    rx_if_bridge_i = re.compile(
        r"\t\s+ifmaxaddr \d+ port (?P<ifindex>\d+) priority \d+")

    def add_iface(self):
        if "type" in self.iface:
            if not self.parent:
                self.iface["subinterfaces"] = []
                self.iface["subinterfaces"] += [self.subiface]
                self.interfaces += [self.iface]
            else:
                if self.parent == "IEEE 802.11":
                    for i in self.interfaces:
                        if "mac" in i:
                            if i["mac"] == self.subiface["mac"]:
                                i["subinterfaces"] += [self.subiface]
                                break
                else:
                    for i in self.interfaces:
                        if i["name"] == self.parent:
                            i["subinterfaces"] += [self.subiface]
                            break
        self.iface = {}
        self.subiface = {}
        self.parent = ""

    def execute(self):
        self.portchannel = self.scripts.get_portchannel()
        self.if_stp = []
        self.interfaces = []
        self.iface = {}
        self.subiface = {}
        self.parent = ""
        self.snmp_ifindex = 0
        for s in self.cli("ifconfig -v", cached=True).splitlines():
            match = self.rx_if_name.search(s)
            if match:
                self.snmp_ifindex += 1
                self.add_iface()
                flags = match.group("flags")
                self.iface["name"] = match.group("ifname")
                self.subiface["name"] = match.group("ifname")
                self.iface["admin_status"] = flags.startswith("UP,")
                self.subiface["admin_status"] = flags.startswith("UP,")
                self.subiface["enabled_afi"] = []
                self.subiface["mtu"] = int(match.group("mtu"))
                self.iface["snmp_ifindex"] = self.snmp_ifindex
                self.iface["enabled_protocols"] = []
                if "LOOPBACK" in flags:
                    self.iface["type"] = "loopback"
                    self.iface["oper_status"] = flags.startswith("UP,")
                    self.subiface["oper_status"] = flags.startswith("UP,")
                if "POINTOPOINT" in flags:
                    self.iface["type"] = "tunnel"
                continue
            match = self.rx_if_descr.search(s)
            if match:
                self.iface["descriptions"] = match.group("descr")
                self.subiface["descriptions"] = match.group("descr")
                continue
            match = self.rx_if_mac.search(s)
            if match:
                self.iface["mac"] = match.group("mac")
                self.subiface["mac"] = match.group("mac")
                self.iface["type"] = "physical"
                continue
            match = self.rx_if_inet.search(s)
            if match:
                ip = match.group("inet")
                netmask = match.group("netmask")
                mask = IPv4._to_prefix(int(netmask, 16), 32).address
                mask = IPv4.netmask_to_len(mask)
                ipv4_addr = "%s/%s" % (ip, mask)
                if "ipv4_addresses" in self.subiface:
                    self.subiface["ipv4_addresses"] += [ipv4_addr]
                else:
                    self.subiface["ipv4_addresses"] = [ipv4_addr]
                    self.subiface["enabled_afi"] += ["IPv4"]
                continue
            match = self.rx_if_inet6.search(s)
            if match:
                ipv6 = match.group("inet6")
                if ipv6.find("%") >= 0:
                    continue
                prefixlen = match.group("prefixlen")
                ipv6_addr = "%s/%s" % (ipv6, prefixlen)
                if "ipv6_addresses" in self.subiface:
                    self.subiface["ipv6_addresses"] += [ipv6_addr]
                else:
                    self.subiface["ipv6_addresses"] = [ipv6_addr]
                    self.subiface["enabled_afi"] += ["IPv6"]
                continue
            match = self.rx_if_status.search(s)
            if match:
                self.iface["oper_status"] = True
                self.subiface["oper_status"] = True
                continue
            match = self.rx_if_vlan.search(s)
            if match:
                self.subiface.update({
                    "vlan_ids": [int(match.group("vlan"))]
                })
                self.parent = match.group("parent")
                continue
            for i in self.portchannel:
                if self.iface["name"] == i["interface"]:
                    self.iface["type"] = "aggregated"
                    #self.subiface["enabled_afi"] = ["BRIDGE"]
                if self.iface["name"] in i["members"]:
                    if i["type"] == "L" and \
                    not "LACP" in self.iface["enabled_protocols"]:
                        self.iface["enabled_protocols"] += ["LACP"]
                    self.iface["aggregated_interface"] = i["interface"]
            match = self.rx_if_wlan.search(s)
            if match:
                self.parent = "IEEE 802.11"
                continue
            match = self.rx_if_bridge.search(s)
            if match:
                self.iface["type"] = "SVI"
                if not "BRIDGE" in self.subiface["enabled_afi"]:
                    self.subiface["enabled_afi"] += ["BRIDGE"]
                continue
            match = self.rx_if_bridge_m.search(s)
            if match:
                ifname = match.group("ifname")
                continue
            match = self.rx_if_bridge_i.search(s)
            if match:
                caps = {
                    "name": ifname,
                    "ifindex": match.group("ifindex"),
                    "parent": self.iface["name"]
                }
                match = self.rx_if_bridge_s.search(s)
                if match:
                    caps["STP"] = True
                self.if_stp += [caps]
        self.add_iface()
        if len(self.if_stp) > 0:
            for i in self.interfaces:
                for s in self.if_stp:
                    if i["name"] == s["name"]:
                        # For verify
                        i["snmp_ifindex"] = int(s["ifindex"])
                        i["aggregated_interface"] = s["parent"]
                    if "STP" in s:
                        i["enabled_protocols"] += ["STP"]
        return [{"interfaces": self.interfaces}]
