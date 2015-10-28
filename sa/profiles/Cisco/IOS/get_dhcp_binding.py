# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdhcpbinding import IGetDHCPBinding
import re
import datetime


class Script(BaseScript):
    name = "Cisco.IOS.get_dhcp_binding"
    interface = IGetDHCPBinding
    rx_line = re.compile(r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<expire>.+?)\s+(?P<type>Automatic|Manual)$", re.IGNORECASE)

    def execute(self):
        data = self.cli("show ip dhcp binding")
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip().lower())
            if match:
                d = match.group("expire")
                if d == "infinite":
                    expire = d
                else:
                    expire = datetime.datetime.strptime(d, "%b %d %Y %I:%M %p")
                r.append({
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "expiration": expire,
                    "type": match.group("type")[0].upper(),
                })
        return r
