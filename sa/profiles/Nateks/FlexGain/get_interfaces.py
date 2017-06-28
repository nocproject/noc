# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.FlexGain.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Nateks.FlexGain.get_interfaces"
    interface = IGetInterfaces

    rx_mac = re.compile(
        "(?P<ifname>.+):\s*MAC Address\s+:(?P<mac>\S+)", re.MULTILINE)
    rx_vlan = re.compile(
        "(?P<vlan_id>\d+)\s+(?P<ifname>\S+)\s+(?P<state>Tagged|unTagged)")
    rx_vpivci = re.compile(
        "\s+\d+\s+(?P<vpi>\d+)/(?P<vci>\d+)\s+(?P<pvid>\d+)\s+\d+")
    rx_ge = re.compile(
        "^(?P<ifname>Gigabit Ethernet\s+\d+)\s*,\s*Index\s*:\s+(?P<ifindex>\d+)",
        re.MULTILINE)
    rx_status = re.compile(
        r"Port\s*:\s*Admin/Oper:(?P<admin_status>On|Off)/(?P<oper_status>On|Off)")
    rx_xdsl = re.compile(
        "^Slot\s*:\s*(?P<slot>\d+),\s*Port:\s*(?P<port>\d+)\s*,\s*"
        "Bridge\s*:\s*(?P<bridge>\d+)\s*,\s*Index\s*:\s*(?P<ifindex>\d+)",
        re.MULTILINE)
    rx_ip = re.compile(
        r"Management Port IP Address\s*:\s*(?P<ip>\S+)\s*/\s*(?P<mask>\S+)")
    rx_mgmt_vlan = re.compile(
        r"management allow VLAN ID\s*:\s*(?P<vlan_id>\d+)")

    def execute(self):
        ifmacs = {}
        for l in self.cli("show system information", cached=True).split("\n"):
            match = self.rx_mac.search(l)
            if match:
                ifmacs[self.profile.convert_interface_name(
                    match.group("ifname"))] = match.group("mac")
        vlans = []
        for l in self.cli("show vlan").split("\n"):
            match = self.rx_vlan.search(l)
            if match:
                vlans += [{
                    "vlan_id": match.group("vlan_id"),
                    "ifname": match.group("ifname"),
                    "tagged": match.group("state") == "Tagged"
                }]
        interfaces = []
        for l in self.cli("show interface counter").split("\n"):
            match = self.rx_ge.search(l)
            if match:
                ifname = self.profile.convert_interface_name(match.group("ifname"))
                v = self.cli("show interface gigabit %s" % ifname[-1])
                match1 = self.rx_status.search(v)
                oper_status = bool(match1.group("oper_status") == "On")
                admin_status = bool(match1.group("admin_status") == "On")
                i = {
                    "name": ifname,
                    "type": "physical",
                    "oper_status": oper_status,
                    "admin_status": admin_status,
                    "enabled_protocols": [],
                    "snmp_ifindex": int(match.group("ifindex")),
                    "subinterfaces": [{
                        "name": ifname,
                        "oper_status": oper_status,
                        "admin_status": admin_status,
                        "enabled_afi": ['BRIDGE']
                    }]
                }
                if ifname in ifmacs:
                    i["mac"] = ifmacs[ifname]
                    i["subinterfaces"][0]["mac"] = ifmacs[ifname]
                for v in vlans:
                    if v["ifname"] == ifname:
                        if v["tagged"] == True:
                            if v["vlan_id"] == "1":
                                continue
                            if "tagged_vlans" in i["subinterfaces"][0]:
                                i["subinterfaces"][0]["tagged_vlans"] += [int(v["vlan_id"])]
                            else:
                                i["subinterfaces"][0]["tagged_vlans"] = [int(v["vlan_id"])]
                        else:
                            i["subinterfaces"][0]["untagged_vlan"] = int(v["vlan_id"])
                interfaces += [i]
            match = self.rx_xdsl.search(l)
            if match:
                ifname = "%s/%s/%s" % (match.group("slot"), \
                match.group("port"), match.group("bridge"))
                v = self.cli("show interface xdsl %s" % ifname[:-2])
                match1 = self.rx_status.search(v)
                oper_status = bool(match1.group("oper_status") == "On")
                admin_status = bool(match1.group("admin_status") == "On")
                i = {
                    "name": ifname,
                    "type": "physical",
                    "oper_status": oper_status,
                    "admin_status": admin_status,
                    "enabled_protocols": [],
                    "snmp_ifindex": int(match.group("ifindex")),
                    "subinterfaces": []
                }
                for l1 in v.split("\n"):
                    match1 = self.rx_vpivci.search(l1)
                    if match1:
                        i["subinterfaces"] += [{
                            "name": ifname,
                            "oper_status": oper_status,
                            "admin_status": admin_status,
                            "enabled_afi": ['BRIDGE', 'ATM'],
                            "vlan_ids": [int(match1.group("pvid"))],
                            "vpi": int(match1.group("vpi")),
                            "vci": int(match1.group("vci"))
                        }]
                interfaces += [i]
        v = self.cli("show management gbe")
        i = {
            "name": "gbe",
                "type": "SVI",
                "oper_status": True,
                "admin_status": True,
                "subinterfaces": [{
                    "name": "gbe",
                    "oper_status": True,
                    "admin_status": True,
                    "enabled_afi": ['IPv4']
                }]
            }
        for l in v.split("\n"):
            match = self.rx_ip.search(l)
            if match:
                ip_address = match.group("ip")
                ip_subnet = match.group("mask")
                ip_address = "%s/%s" % (
                    ip_address, IPv4.netmask_to_len(ip_subnet))
                i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            match = self.rx_mgmt_vlan.search(l)
            if match:
                i["subinterfaces"][0]["vlan_ids"] = [int(match.group("vlan_id"))]
        interfaces += [i]
        v = self.cli("show management mgmt")
        i = {
            "name": "mgmt",
                "type": "management",
                "oper_status": True,
                "admin_status": True,
                "subinterfaces": [{
                    "name": "mgmt",
                    "oper_status": True,
                    "admin_status": True,
                    "enabled_afi": ['IPv4']
                }]
            }
        for l in v.split("\n"):
            match = self.rx_ip.search(l)
            if match:
                ip_address = match.group("ip")
                ip_subnet = match.group("mask")
                ip_address = "%s/%s" % (
                    ip_address, IPv4.netmask_to_len(ip_subnet))
                i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
        interfaces += [i]
        return [{"interfaces": interfaces}]
