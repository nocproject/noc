# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DFL.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "DLink.DFL.get_arp"
    interface = IGetARP
    rx_iface = re.compile(r"^ARP cache of iface (?P<interface>\S+)")
    rx_line = re.compile(r"^\s+\S+\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+=\s+(?P<mac>\S+)\s+Expire=\d+$", re.MULTILINE)

    def execute(self):
        r = []
        iface = ""
        for l in self.cli("arp").splitlines():
            match_iface = self.rx_iface.match(l)
            if match_iface:
                iface = match_iface.group("interface")
            match_line = self.rx_line.match(l)
            if match_line:
                ip = match_line.group("ip")
                mac = match_line.group("mac")
                if iface:
                    r += [{"ip": ip, "mac": mac, "interface": iface}]
        return r
