# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "Orion.NOS.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)\s+",
        re.MULTILINE)
    rx_descr = re.compile(
        r"^(?P<port>\d+)(?P<descr>.+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_switchport = re.compile(
        r"^Administrative Mode: (?P<mode>\S+)\s*\n"
        r"^Operational Mode: \S+\s*\n"
        r"^Access Mode VLAN: (?P<access_vlan>\d+)\s*\n"
        r"^Administrative Access Egress VLANs: \S+\s*\n"
        r"^Operational Access Egress VLANs: \S+\s*\n"
        r"^Trunk Native Mode VLAN: (?P<native_vlan>\d+)\s*\n"
        r"(^Trunk Native VLAN: \S+\s*\n)?"
        r"^Administrative Trunk Allowed VLANs: (?P<vlans>\S+)\s*\n",
        re.MULTILINE)
    rx_enabled = re.compile(
        r"^\s*(?P<port>d+)\s+Ena",
        re.MULTILINE | re.IGNORECASE)
    # do not verified
    rx_oam = re.compile(
        r"^\s*(?P<port>d+)operate",
        re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<ip_address>\S+)\s+(?P<ip_subnet>\S+)\s+"
        r"(?P<vlan_id>\d+)\s+(?P<admin_status>\S+)\s*\n", re.MULTILINE)

    def get_gvrp(self):
        try:
            v = self.cli("show gvrp configuration")
            if "GVRP Global Admin State: Disable" not in v:
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_stp(self):
        # Need more examples
        return []
        try:
            v = self.cli("show spanning-tree")
            return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []

    def get_ctp(self):
        try:
            v = self.cli("show loopback-detection")
            if "Loopback detection: Disabled" not in v:
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_lldp(self):
        try:
            v = self.cli("show lldp statistic")
            if "LLDP is not enabled." not in v:
                # Need more examples
                return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def get_oam(self):
        try:
            # Need more examples
            v = self.cli("show extended-oam status")
            return self.rx_enabled.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def execute(self):
        interfaces = []
        descr = []
        gvrp = self.get_gvrp()
        stp = self.get_stp()
        ctp = self.get_ctp()
        lldp = self.get_lldp()
        oam = self.get_lldp()
        for l in self.cli("show interface port description").split("\n"):
            match = self.rx_descr.match(l.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]
        for match in self.rx_port.finditer(self.cli("show interface port")):
            ifname = match.group("port")
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": "enable" in match.group("admin_status"),
                "oper_status": match.group("oper_status") != "down",
                "enabled_protocols": [],
                "snmp_ifindex": ifname,
                "subinterfaces": []
            }
            if ifname in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            if ifname in stp:
                iface["enabled_protocols"] += ["STP"]
            if ifname in ctp:
                iface["enabled_protocols"] += ["CTP"]
            if ifname in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            if ifname in oam:
                iface["enabled_protocols"] += ["OAM"]
            sub = {
                "name": ifname,
                "admin_status": "enable" in match.group("admin_status"),
                "oper_status": match.group("oper_status") == "!=",
                "enabled_afi": ["BRIDGE"],
                "tagged_vlans": []
            }
            for i in descr:
                if ifname == i["port"]:
                    iface["description"] = i["descr"]
                    sub["description"] = i["descr"]
                    break
            s = self.cli("show interface port %s switchport" % ifname)
            match1 = self.rx_switchport.search(s)
            if match1.group("mode") == "access":
                sub["untagged_vlan"] = int(match1.group("access_vlan"))
            elif match1.group("mode") == "trunk":
                sub["untagged_vlan"] = int(match1.group("native_vlan"))
                sub["tagged_vlans"] = \
                self.expand_rangelist(match1.group("vlans"))
            else:
                raise self.NotSupportedError()
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        mac = self.profile.get_version(self)["mac"]
        descr = []
        for l in self.cli("show interface ip description").split("\n"):
            match = self.rx_descr.match(l.strip())
            if match:
                if match.group("port") == "Port":
                    continue
                descr += [match.groupdict()]


        v = self.cli("show interface ip")
        for match in self.rx_ip.finditer(v):
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (
                ip_address, IPv4.netmask_to_len(ip_subnet))
            ifname = match.group("ifname")
            iface = {
                "name": "ip%s" % ifname,
                "type": "SVI",
                "admin_status": match.group("admin_status") == "active",
                "oper_status": match.group("admin_status") == "active",
                "mac": mac,
                "subinterfaces": [{
                    "name":  "ip%s" % ifname,
                    "admin_status": match.group("admin_status") == "active",
                    "oper_status": match.group("admin_status") == "active",
                    "mac": mac,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": [int(match.group("vlan_id"))]
                }]
            }
            for i in descr:
                if ifname == i["port"]:
                    iface["description"] = i["descr"]
                    iface["subinterfaces"][0]["description"] = i["descr"]
                    break
            interfaces += [iface]
            # Not implemented
            # v = self.cli("show interface ipv6")
        return [{"interfaces": interfaces}]
