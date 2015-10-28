# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdhcpbinding import IGetDHCPBinding
import re
import datetime
import time


class Script(BaseScript):
    name = "EdgeCore.ES.get_dhcp_binding"
    interface = IGetDHCPBinding
    rx_line = re.compile(r"^(?P<mac>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<expire>.+?)\s+(?P<type>dhcp-snooping)\s+(?P<vlan>\d+)\s+(?P<interface>.+?)$", re.IGNORECASE)

    def execute(self):
        try:
            data = self.cli("show ip dhcp snooping binding")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        now = datetime.datetime.now()
        basetimestamp = int(time.mktime(now.timetuple()))
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip().lower())
            if match:
                d = match.group("expire")
                if d == "infinite":
                    expire = d
                else:
                    expire = datetime.datetime.fromtimestamp(basetimestamp + int(d))
                r.append({
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "expiration": expire,
                    "type": "A"  # Automatic
                })
        return r
