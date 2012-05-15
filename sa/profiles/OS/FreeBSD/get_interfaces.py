# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_interfaces"
    implements = [IGetInterfaces]
    rx_if_name = re.compile(
        r"^(?P<ifname>\S+): flags=\d+<(?P<flags>\S+)> metric \d+ mtu \d+$")
    rx_if_up = re.compile(
        r"^(?P<ifname>\S+): flags=\d+<UP,\S+> metric \d+ mtu \d+$")
    rx_if_descr = re.compile(r"^\tdescription: (?P<descr>.+)\s*$")
    rx_if_mac = re.compile(r"^\tether (?P<mac>\S+)\s*$")
    rx_if_inet = re.compile(
        r"^\tinet (?P<inet>\S+) netmask (?P<netmask>\S+)\s*(broadcast .+)?$")
    rx_if_inet6 = re.compile(r"^\tinet6 (?P<inet6>\S+) prefixlen (?P<prefixlen>\S+)\s*(scopeid .+)?$")
    rx_if_status = re.compile(
        r"^\tstatus: (?P<status>active|associated|running|inserted)\s*$")
    rx_if_vlan = re.compile(
        r"^\tvlan: (?P<vlan>\d+) parent interface: (?P<parent>\S+)$")
    rx_if_lagg = re.compile(r"^\tlaggport: (?P<ifname>\S+) flags=\d+<.*>$")
    rx_if_wlan = re.compile(r"^\tssid .+$")
    interfaces = []
    iface = {}
    subiface = {}
    parent = ""

    def add_iface(self):
        if "type" in self.iface:
            if not self.parent:
                self.iface.update({"subinterfaces": []})
                self.iface["subinterfaces"] += [self.subiface]
                self.interfaces += [self.iface]
            else:
                if self.parent == "IEEE 802.11":
                    for i in self.interfaces:
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
        r = [{"interfaces": []}]
        for s in self.cli("ifconfig -v").splitlines():
            match = self.rx_if_name.search(s)
            if match:
                self.add_iface()
                flags = match.group("flags")
                self.iface.update({"name": match.group("ifname")})
                self.subiface.update({"name": match.group("ifname")})
                self.iface.update({"admin_status": flags.startswith("UP,")})
                self.subiface.update({"admin_status": flags.startswith("UP,")})
                if flags.find("LOOPBACK") >= 0:
                    self.iface.update({"type": "loopback"})
                if flags.find("POINTOPOINT") >= 0:
                    self.iface.update({"type": "tunnel"})
                continue
            match = self.rx_if_descr.search(s)
            if match:
                self.iface.update({"descriptions": match.group("descr")})
                self.subiface.update({"descriptions": match.group("descr")})
                continue
            match = self.rx_if_mac.search(s)
            if match:
                self.iface.update({"mac": match.group("mac")})
                self.subiface.update({"mac": match.group("mac")})
                self.iface.update({"type": "physical"})
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
                    self.subiface.update({"ipv4_addresses": [ipv4_addr]})
                    self.subiface.update({"is_ipv4": True})
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
                    self.subiface.update({"ipv6_addresses": [ipv6_addr]})
                    self.subiface.update({"is_ipv6": True})
                continue
            match = self.rx_if_status.search(s)
            if match:
                self.iface.update({"oper_status": True})
                self.subiface.update({"oper_status": True})
                continue
            match = self.rx_if_vlan.search(s)
            if match:
                self.subiface.update({
                    "vlan_ids": [int(match.group("vlan"))]
                })
                self.parent = match.group("parent")
                continue
            match = self.rx_if_lagg.search(s)
            if match:
                ifname = match.group("ifname")
                if "aggregated_interface" in self.iface:
                    self.iface["aggregated_interface"] += [ifname]
                else:
                    self.iface.update({"aggregated_interface": [ifname]})
                    self.iface.update({"is_lacp": True})
                continue
            match = self.rx_if_wlan.search(s)
            if match:
                self.parent = "IEEE 802.11"
                continue
        self.add_iface()
        r[0]["interfaces"] = self.interfaces
        return r
