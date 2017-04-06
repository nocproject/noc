# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.DSLAM.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4

import re


class Script(BaseScript):
    name = "Eltex.DSLAM.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        "^\s+(?P<port>\S+)\s+:\s+(?P<descr>.+)\n", re.MULTILINE)
    rx_ip = re.compile(
        "^\s+Control vid:\s+(?P<vlan_id>\d+)\s*\n"
        "^\s+IP address:\s+(?P<ip_address>\d+\S+)\s*\n"
        "^\s+Server IP:\s+\S+\s*\n"
        "^\s+MAC address:\s+(?P<mac>\S+)\s*\n"
        "^\s+Netmask:\s+(?P<ip_subnet>\d+\S+)\s*\n", re.MULTILINE)

    def execute(self):
        interfaces = []
        cmd = self.cli("switch show port description")
        for match in self.rx_port.finditer(cmd):
            ifname = match.group("port")
            if ifname == "cpu":
                iface = {
                    "name": ifname,
                    "type": "SVI",
                    "subinterfaces": [{
                        "name": ifname,
                        "enabled_afi": ["IPv4"],
                    }]
                }
                match = self.rx_ip.search(self.cli("system show net settings"))
                ip_address = match.group("ip_address")
                ip_subnet = match.group("ip_subnet")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                iface['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
                iface['subinterfaces'][0]["vlan_ids"] = [match.group("vlan_id")]
                iface['mac'] = match.group("mac")
                iface['subinterfaces'][0]["mac"] = match.group("mac")
            else:
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "subinterfaces": [{
                        "name": ifname,
                        "enabled_afi": ["BRIDGE"],
                    }]
                }
            interfaces += [iface]
        return [{"interfaces": interfaces}]
