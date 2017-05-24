# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.lib.text import list_to_ranges

import re


class Script(BaseScript):
    name = "Eltex.LTE.get_interfaces"
    interface = IGetInterfaces

    rx_mac1 = re.compile(
        r"^Port (?P<port>\d+) MAC address: (?P<mac>\S+)", re.MULTILINE)
    rx_mac2 = re.compile(r"MAC address:\s*\n^\s+(?P<mac>\S+)", re.MULTILINE)
    rx_vlan = re.compile(
        r"^Interface (?P<port>\d+)\s*\n"
        r"^\s+PVID:\s+\d+\s*\n"
        r"^\s+Frame types:\s+\S+\s*\n"
        r"^\s+Ingress filtering:\s+\S+\s*\n"
        r"^\s+Member of VLANs:\s*\n"
        r"^\s+tagged:\s+(?P<tagged>.+)\n"
        r"^\s+untagged:\s+(?P<untagged>\d+|none)",
        re.MULTILINE | re.DOTALL)

    rx_ip = re.compile(r"\n\nIP address:\s+(?P<ip>\d+\S+)")
    rx_mgmt_ip = re.compile(
        r"^Management interface: \((?P<state>\S+)\)\s*\n"
        r"^IP address:\s+(?P<ip>\d+\S+)\s*\n"
        r"^VID:\s+(?P<vlan_id>\d+|none)", re.MULTILINE)

    def execute(self):
        interfaces = []
        macs = {}
        tagged_vlans = {}
        untagged_vlans = {}
        with self.profile.switch(self):
            cmd = self.cli("show interfaces mac-address")
            for match in self.rx_mac1.finditer(cmd):
                macs[match.group("port")] = match.group("mac")
            cmd = self.cli("show interfaces vlans")
            for l in self.cli("show interfaces vlans").split("\n\n"):
                match = self.rx_vlan.search(l)
                if match:
                    if match.group("tagged") != "none":
                        tagged_vlans[match.group("port")] = \
                            self.expand_rangelist(match.group("tagged"))
                    if match.group("untagged") != "none":
                        untagged_vlans[match.group("port")] = \
                            match.group("untagged")
            cmd = self.cli("show version")
            match = self.rx_mac2.search(cmd)
            if match:
                ip_mac = match.group("mac")
            else:
                ip_mac = ""
        ports = self.scripts.get_interface_status()
        for i in ports:
            iface = {
                "name": i["interface"],
                "type": "physical",
                "oper_status": i["status"],
                "mac": macs[i["interface"]],
                "subinterfaces": [{
                    "name": i["interface"],
                    "oper_status": i["status"],
                    "enabled_afi": ["BRIDGE"],
                    "mac": macs[i["interface"]]
                }]
            }
            t = tagged_vlans.get(i["interface"])
            if t:
                iface["subinterfaces"][0]["tagged_vlans"] = t
            u = untagged_vlans.get(i["interface"])
            if u:
                iface["subinterfaces"][0]["untagged_vlan"] = u
            interfaces += [iface]
        cmd = self.cli("show system information")
        match = self.rx_ip.search(cmd)
        if match:
            iface = {
                "name": "ip",
                "type": "SVI",
                "subinterfaces": [{
                    "name": "ip",
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [match.group("ip")]
                }]
            }
            if ip_mac:
                iface["mac"] = ip_mac
                iface["subinterfaces"][0]["mac"] = ip_mac
            interfaces += [iface]
        match = self.rx_mgmt_ip.search(cmd)
        if match:
            iface = {
                "name": "mgmt",
                "type": "management",
                "oper_status": match.group("state") == "enabled",
                "admin_status": match.group("state") == "enabled",
                "subinterfaces": [{
                    "name": "mgmt",
                    "oper_status": match.group("state") == "enabled",
                    "admin_status": match.group("state") == "enabled",
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [match.group("ip")]
                }]
            }
            if match.group("vlan_id") != "none":
                iface["subinterfaces"][0]["vlan_ids"] = [match.group("vlan_id")]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
