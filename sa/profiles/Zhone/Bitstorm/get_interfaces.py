# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Zhone.Bitstorm.get_interfaces"
    interface = IGetInterfaces

    rx_eth = re.compile(
        r"^\s*Port (?P<port>eth\d+) Configuration\s*\n"
        r"^\s*\n"
        r"(^\s*state \(admin status\)\s+(?P<admin_status>up|down)\s*\n)?"
        r"^\s*connector\s+\S+\s*\n"
        r"^\s*mode\s+\S+\s*\n"
        r"^\s*rate\s+\S+\s*\n"
        r"^\s*flow-control\s+\S+\s*\n"
        r"^\s*xover\s+\S+\s*\n"
        r"^\s*pvid\s+(?P<vlan_id>\d+)\s*\n",
        re.MULTILINE
    )
    rx_dsl = re.compile(
        r"^(?P<port>\d+) Configuration\s*\n"
        r"^\s*\n"
        r"(^\s*name(?P<name>.*)\n)?"
        r"(^\s*state\s+(?P<admin_status>enabled|disabled)\s*\n)?",
        re.MULTILINE
    )
    rx_dsl_vpi_vci = re.compile(
        r"^\s*(?P<name>\d+)\s+(?P<vpi>\d+)/(?P<vci>\d+)\s+llc-bridged\s+"
        r"((?P<vlan_ids>\d+(, \d+)*)\s*)?\S*\s*\n",
        re.MULTILINE
    )
    rx_inband = re.compile(
        r"^Inband Management Address (?P<ifnum>\d+):\s*\n"
        r"^\s*ip address\s+(?P<ip>\S+)( \((?:dhcp|bootp)\))?\s*\n"
        r"^\s*subnet mask\s+(?P<mask>\S+)\s*\n"
        r"^\s*Vlan ID\s+(?P<vlan_id>\d+)\s*\n"
        r"^\s*port status\s+(?P<admin_status>enable|disable)\s*\n"
        r"^\s*MAC Address\s+(?P<mac>\S+)\s*\n",
        re.MULTILINE
    )
    rx_inband2 = re.compile(
        r"^\s*ip address\s+(?P<ip>\S+)( \((?:dhcp|bootp)\))?\s*\n"
        r"^\s*subnet mask\s+(?P<mask>\S+)\s*\n"
        r"^\s*MAC Address\s+(?P<mac>\S+)\s*\n",
        re.MULTILINE
    )
    rx_outband = re.compile(
        r"^\s*ip address\s+(?P<ip>\S+)( \((?:dhcp|bootp)\))?\s*\n"
        r"^\s*subnet mask\s+(?P<mask>\S+)\s*\n"
        r"^\s*MAC Address\s+(?P<mac>\S+)\s*\n"
        r"(^\s*Port Status\s+(?P<admin_status>enable|disable)\s*\n)?",
        re.MULTILINE
    )
    rx_vlan = re.compile(
        r"^VLAN\s+(?P<vlan_id>\d+)\s*\n"
        r"^\s*Name.*\n"
        r"^\s*Tagged Members(?P<tagged>.*)\n"
        r"^\s*UnTagged Members(?P<untagged>.*)\n",
        re.MULTILINE
    )

    def execute(self):
        interfaces = []
        v = self.cli("show interface ethernet all configuration")
        for match in self.rx_eth.finditer(v):
            iface = {
                "name": match.group('port'),
                "type": "physical",
                "subinterfaces": [{
                    "name": match.group('port'),
                    "enabled_afi": ["BRIDGE"],
                }]
            }
            if int(match.group('vlan_id')) > 0:
                iface["subinterfaces"][0]["untagged_vlan"] = int(match.group('vlan_id'))
            if "admin_status" in match.groupdict():
                iface["admin_status"] = match.group("admin_status") == "up"
                iface["subinterfaces"][0]["admin_status"] = \
                    match.group("admin_status") == "up"
            interfaces += [iface]

        v = self.cli("show interface dsl all configuration")
        for p in v.split("\n DSL Port "):
            match = self.rx_dsl.search(p)
            if not match:
                continue
            iface = {
                "name": match.group("port"),
                "type": "physical",
                "subinterfaces": []
            }
            if match.group("admin_status"):
                iface["admin_status"] = match.group("admin_status") == "enabled"
            if match.group("name") and match.group("name").strip():
                iface["description"] = match.group("name").strip()
            for match in self.rx_dsl_vpi_vci.finditer(p):
                sub = match.groupdict()
                sub["name"] = "%s/%s" % (iface["name"], sub["name"])
                sub["admin_status"] = iface["admin_status"]
                sub["enabled_afi"] = ["BRIDGE", "ATM"]
                if sub["vlan_ids"]:
                    sub["vlan_ids"] = [
                        int(x) for x in sub["vlan_ids"].split(", ") if int(x) > 0
                    ]
                iface["subinterfaces"] += [sub]

            interfaces += [iface]

        v = self.cli("show management inband")
        for match in self.rx_inband.finditer(v):
            iface = {
                "name": "mgmt_i" + match.group('ifnum'),
                "admin_status": match.group("admin_status") == "enable",
                "type": "SVI",
                "mac": match.group("mac"),
                "subinterfaces": [{
                    "name": "mgmt_i" + match.group('ifnum'),
                    "admin_status": match.group("admin_status") == "enable",
                    "mac": match.group("mac")
                }]
            }
            if match.group("ip") != "0.0.0.0":
                ip = match.group("ip")
                mask = match.group("mask")
                ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
            if match.group("vlan_id") != "0":
                iface["subinterfaces"][0]["vlan_ids"] = \
                    [match.group("vlan_id")]
            interfaces += [iface]

        match = self.rx_inband2.search(v)
        if match:
            iface = {
                "name": "mgmt_i",
                "type": "SVI",
                "mac": match.group("mac"),
                "subinterfaces": [{
                    "name": "mgmt_i",
                    "mac": match.group("mac")
                }]
            }
            if match.group("ip") != "0.0.0.0":
                ip = match.group("ip")
                mask = match.group("mask")
                ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
            interfaces += [iface]

        v = self.cli("show management out-of-band")
        match = self.rx_outband.search(v)
        iface = {
            "name": "mgmt_o",
            "type": "SVI",
            "mac": match.group("mac"),
            "subinterfaces": [{
                "name": "mgmt_o",
                "mac": match.group("mac")
            }]
        }
        if "admin_status" in match.groupdict():
            iface["admin_status"] = match.group("admin_status") == "enable"
            iface["subinterfaces"][0]["admin_status"] = \
                match.group("admin_status") == "enable"
        if match.group("ip") != "0.0.0.0":
            ip = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
        interfaces += [iface]

        v = self.cli("show vlan configuration all")
        for match in self.rx_vlan.finditer(v):
            vlan_id = match.group("vlan_id")
            if int(vlan_id) < 1:
                continue
            tagged = match.group("tagged").strip()
            if tagged:
                tagged = tagged.split(", ")
                for i in interfaces:
                    sub = i["subinterfaces"][0]
                    if sub["name"] not in tagged:
                        continue
                    if "tagged_vlans" in sub:
                        sub["tagged_vlans"] += [vlan_id]
                    else:
                        sub["tagged_vlans"] = [vlan_id]
            untagged = match.group("untagged").strip()
            if untagged:
                untagged = untagged.split(", ")
                for i in interfaces:
                    sub = i["subinterfaces"][0]
                    if sub["name"] not in untagged:
                        continue
                    sub["untagged_vlan"] = vlan_id

        return [{"interfaces": interfaces}]
