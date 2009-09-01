# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetDHCPBinding
import re,datetime

rx_line=re.compile(r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<expire>.+?)\s+(?P<type>Automatic|Manual)$",re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_dhcp_binding"
    implements=[IGetDHCPBinding]
    def execute(self):
        self.cli("terminal length 0")
        data=self.cli("show ip dhcp binding")
        r=[]
        for l in data.split("\n"):
            match=rx_line.match(l.strip().lower())
            if match:
                d=match.group("expire")
                if d=="infinite":
                    expire=d
                else:
                    expire=datetime.datetime.strptime(d,"%b %d %Y %I:%M %p")
                r.append({
                    "ip"         : match.group("ip"),
                    "mac"        : match.group("mac"),
                    "expiration" : expire,
                    "type"       : match.group("type")[0].upper(),
                })
        return r
