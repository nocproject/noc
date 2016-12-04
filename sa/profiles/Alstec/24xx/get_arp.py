# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alstec.ALS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Alstec.ALS.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^vlan \d+\s+(?P<interface>\S+)\s+"
        r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+\S+\s*$", re.MULTILINE)

    rx_line1 = re.compile(
        r"^IP\sAddress\.+\s(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s*", re.MULTILINE
    )

    rx_line2 = re.compile(
        r"MAC\sAddress\.+\s(?P<MAC_address>\S+)\n", re.MULTILINE
    )

    def execute(self, interface=None):
        r = []
        v = self.cli("show network")
        # for match in self.rx_line.finditer(self.cli("show management")):
        #    if (interface is not None) \
        #    and (interface != match.group("interface")):
        #        continue
        #    r += [match.groupdict()]
        ip = self.rx_line1.findall(v)
        mac = self.rx_line2.findall(v)
        r = [{"ip": ip[0], "mac": mac[0]}]
        return r
