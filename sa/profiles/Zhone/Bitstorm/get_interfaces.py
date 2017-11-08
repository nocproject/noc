# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.core.ip import IPv4
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


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
    rx_inband = re.compile(
        r"^Inband Management Address (?P<ifnum>\d+):\s*\n"
        r"^\s*ip address\s+(?P<ip>\S+)( \(dhcp\))?\s*\n"
        r"^\s*subnet mask\s+(?P<mask>\S+)\s*\n"
        r"^\s*Vlan ID\s+(?P<vlan_id>\d+)\s*\n"
        r"^\s*port status\s+(?P<admin_status>enable|disable)\s*\n"
        r"^\s*MAC Address\s+(?P<mac>\S+)\s*\n",
        re.MULTILINE
    )
    rx_inband2 = re.compile(
        r"^\s*ip address\s+(?P<ip>\S+)( \(dhcp\))?\s*\n"
        r"^\s*subnet mask\s+(?P<mask>\S+)\s*\n"
        r"^\s*MAC Address\s+(?P<mac>\S+)\s*\n",
        re.MULTILINE
    )
    rx_outband = re.compile(
        r"^\s*ip address\s+(?P<ip>\S+)( \(dhcp\))?\s*\n"
        r"^\s*subnet mask\s+(?P<mask>\S+)\s*\n"
        r"^\s*MAC Address\s+(?P<mac>\S+)\s*\n"
        r"(^\s*Port Status\s+(?P<admin_status>enable|disable)\s*\n)?",
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
                    "untagged_vlan": int(match.group('vlan_id'))
                }]
            }
            if "admin_status" in match.groupdict():
                iface["admin_status"] = match.group("admin_status") == "up"
                iface["subinterfaces"][0]["admin_status"] = \
                    match.group("admin_status") == "up"
            interfaces += [iface]

        v = self.cli("show management inband")
        for match in self.rx_inband.finditer(v):
            iface = {
                "name": "inband" + match.group('ifnum'),
                "admin_status": match.group("admin_status") == "enable",
                "type": "SVI",
                "mac": match.group("mac"),
                "subinterfaces": [{
                    "name": "inband" + match.group('ifnum'),
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
                "name": "inband",
                "type": "SVI",
                "mac": match.group("mac"),
                "subinterfaces": [{
                    "name": "inband",
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
            "name": "outband",
            "type": "SVI",
            "mac": match.group("mac"),
            "subinterfaces": [{
                "name": "outband",
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

        return [{"interfaces": interfaces}]
