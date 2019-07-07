# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^\s*(?P<ifname>(?:Eth|vlan)\S+) is (?P<admin_status>\S+), [Ll]ink status is (?P<oper_status>\S+)\s*\n"
        r"^\s*Interface type: \S+\s*\n"
        r"^\s*Interface description:(?P<descr>.+)\n"
        r"^\s*MAC [Aa]ddress: (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_mtu = re.compile(r"^\s*Maximum transmit unit: (?P<mtu>\d+) bytes", re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*VLAN (?P<vlan_id>\d+)\s*\n"
        r"^\s*Name\s*:\s+(?P<name>\S+)\s*\n"
        r"^\s*Tagged Member Ports\s*:(?P<tagged>.*)\n"
        r"^\s*Untagged Member Ports\s*:(?P<untagged>.*)\n",
        re.MULTILINE,
    )
    rx_ip_iface = re.compile(
        r"^\s*Interface (?P<ifname>vlan\d+) is (?P<admin_status>\S+), [Ll]ink status is (?P<oper_status>\S+)\s*\n"
        r"^\s*IP Address is (?P<ip>\S+)",
        re.MULTILINE,
    )

    def execute_cli(self):
        interfaces = []
        v = self.cli("show interfaces")
        for line in v.split("\n\n"):
            match = self.rx_iface.search(line)
            if not match:
                continue
            i = {
                "name": match.group("ifname"),
                "type": "physical",
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "mac": match.group("mac"),
            }
            sub = {
                "name": match.group("ifname"),
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "mac": match.group("mac"),
                "enabled_afi": ["BRIDGE"],
            }
            descr = match.group("descr").strip()
            if descr:
                i["description"] = descr
                sub["description"] = descr
            v1 = self.cli("show lldp interface %s | include Admin Status" % match.group("ifname"))
            if "TX and RX" in v1:
                i["enabled_protocols"] = ["LLDP"]
            match = self.rx_mtu.search(line)
            sub["mtu"] = match.group("mtu")
            i["subinterfaces"] = [sub]
            interfaces += [i]

        v = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(v):
            vlan_id = match.group("vlan_id")
            tagged = self.expand_interface_range(match.group("tagged"))
            untagged = self.expand_interface_range(match.group("untagged"))
            for i in interfaces:
                sub = i["subinterfaces"][0]
                if i["name"][3:] in tagged:
                    if "tagged_vlans" in sub:
                        sub["tagged_vlans"] += [vlan_id]
                    else:
                        sub["tagged_vlans"] = [vlan_id]
                if i["name"][3:] in untagged:
                    sub["untagged_vlan"] = vlan_id

        v = self.cli("show ip interface")
        for line in v.split("\n\n"):
            match = self.rx_ip_iface.search(line)
            if not match:
                continue
            i = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
            }
            sub = {
                "name": match.group("ifname"),
                "admin_status": match.group("admin_status") == "enabled",
                "oper_status": match.group("oper_status") == "up",
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [match.group("ip")],
                "vlan_ids": [match.group("ifname")[4:]],
            }

            v1 = self.cli("show interface %s" % match.group("ifname"))
            match1 = self.rx_iface.search(v1)
            descr = match1.group("descr").strip()
            if descr:
                i["description"] = descr
                sub["description"] = descr
            i["mac"] = match1.group("mac")
            sub["mac"] = match1.group("mac")
            i["subinterfaces"] = [sub]
            interfaces += [i]

        # TODO: show ipv6 interface

        return [{"interfaces": interfaces}]
