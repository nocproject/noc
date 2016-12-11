# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## Alstec.24xx.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Alstec.24xx.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^vlan \d+\s+(?P<interface>\S+)\s+"
        r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+\S+\s*$", re.MULTILINE)

    rx_ip = re.compile(
        r"^IP\sAddress\.+\s(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s*", re.MULTILINE
    )

    rx_mac = re.compile(
        r"MAC\sAddress\.+\s(?P<MAC_address>\S+)\n", re.MULTILINE
    )

    rx_ip_gw = re.compile(
        r"^Default\sGateway\.+\s(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s*", re.MULTILINE
    )

    def execute(self, interface=None):
        r = []
        v = self.cli("show network")

        ip = self.rx_ip.findall(v)
        mac = self.rx_mac.findall(v)
        gw = self.rx_ip_gw.findall(v)

        try:
            macs = parse_table(self.cli("show mac-addr-table vlan 1"))
            mac_gw = macs[0][0]
        except self.CLISyntaxError:
            macs = parse_table(self.cli("show mac-addr-table"))
            print(macs)
            mac_gw = [mac[0] for mac in macs if mac[2] == "1"][0]

        if mac_gw:
            r += [{"ip": gw[0], "mac": mac_gw}]
        r += [{"ip": ip[0], "mac": mac[0]}]

        return r
