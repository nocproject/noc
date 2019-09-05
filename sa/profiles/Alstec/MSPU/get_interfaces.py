# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Alstec.MSPU.get_interfaces"
    interface = IGetInterfaces

    INTERFACE_TYPES = {
        1: "other",
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        0: "physical",  # gigabitEthernet
        53: "SVI",  # propVirtual
    }

    rx_iface = re.compile(
        r"^(?P<ifname>\S+\d+)\s+Link encap:Ethernet\s+HWaddr (?P<mac>\S+)", re.MULTILINE
    )
    rx_flags = re.compile(r"^\s+(?P<flags>.+)\s+MTU:(?P<mtu>\d+)\s+Metric:\d+", re.MULTILINE)
    rx_ip = re.compile(r"^\s+inet addr:(?P<ip>\S+)\s+Bcast:\S+\s+ Mask:(?P<mask>\S+)", re.MULTILINE)
    rx_port_phys = re.compile(r"^\s+(?P<port>(?:adsl|uplink)\d+)\s+(?P<descr>.+)", re.MULTILINE)
    rx_port_status = re.compile(
        r"^\s+admin status: (?P<admin_status>\S+) oper status: (?P<oper_status>\S+)", re.MULTILINE
    )
    rx_mac = re.compile(r"^\s+HWaddr (?P<mac>\S+)", re.MULTILINE)

    def get_phys_iface(self, c, ifname, descr):
        match = self.rx_port_status.search(c)
        oper_status = match.group("oper_status") == "up"
        admin_status = match.group("admin_status") == "up"
        iface = {
            "name": ifname,
            "type": "physical",
            "admin_status": admin_status,
            "oper_status": oper_status,
            "description": descr,
            "subinterfaces": [],
        }
        sub = {
            "name": ifname,
            "admin_status": admin_status,
            "oper_status": oper_status,
            "description": descr,
        }
        match = self.rx_mac.search(c)
        if match:
            iface["mac"] = match.group("mac")
            sub["mac"] = match.group("mac")
        iface["subinterfaces"] += [sub]
        return iface

    def execute_cli(self):
        interfaces = []
        v = self.cli("port adsl adsl", command_submit="\t")
        self.cli("\x01\x0b")  # ^a + ^k
        for match in self.rx_port_phys.finditer(v):
            ifname = match.group("port")
            descr = match.group("descr").strip()
            c = self.cli("port adsl %s show" % ifname)
            iface = self.get_phys_iface(c, ifname, descr)
            interfaces += [iface]
        v = self.cli("port uplink uplink", command_submit="\t")
        self.cli("\x01\x0b")  # ^a + ^k
        for match in self.rx_port_phys.finditer(v):
            ifname = match.group("port")
            descr = match.group("descr").strip()
            c = self.cli("port uplink %s show" % ifname)
            iface = self.get_phys_iface(c, ifname, descr)
            interfaces += [iface]
        for l in self.cli("context ip router ifconfig").split("\n\n"):
            match = self.rx_iface.search(l)
            if not match:
                continue
            ifname = match.group("ifname")
            mac = match.group("mac")
            match = self.rx_flags.search(l)
            oper_status = "RUNNING" in match.group("flags")
            admin_status = "UP " in match.group("flags")
            mtu = match.group("mtu")
            iface = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_status": admin_status,
                "oper_status": oper_status,
                "mac": mac,
                "subinterfaces": [],
            }
            sub = {
                "name": ifname,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "mac": mac,
                "mtu": mtu,
            }
            match = self.rx_ip.search(l)
            if match:
                ip_address = match.group("ip")
                ip_subnet = match.group("mask")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                sub["ipv4_addresses"] = [ip_address]
                sub["enabled_afi"] = ["IPv4"]
            # found = False
            if "." in ifname:
                parent, vlan = ifname.split(".")
                sub["vlan_ids"] = [vlan]
                for i in interfaces:
                    if i["name"] == parent:
                        i["subinterfaces"] += [sub]
                        # found = True
                        break
                continue
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
