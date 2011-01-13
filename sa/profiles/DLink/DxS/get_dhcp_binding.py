# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetDHCPBinding
import re,datetime,time

rx_line=re.compile(r"^(?P<name>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<type>Ethernet)\s+(?P<status>Automatic|Manual)\s+(?P<expire>.+?)",re.IGNORECASE)

class Script(NOCScript):
    name="DLink.DxS.get_dhcp_binding"
    implements=[IGetDHCPBinding]
    def execute(self):
        data=self.cli("show dhcp_binding")
        r=[]
        for l in data.split("\n"):
            match=rx_line.match(l.strip().lower())
            if match:
                d=match.group("expire")
                if d=="infinite":
                    expire=d
                else:
                    expire=datetime.datetime.fromtimestamp(time.time()+int(d))
                r.append({
                    "ip"         : match.group("ip"),
                    "mac"        : match.group("mac"),
                    "expiration" : expire,
                    "type"       : match.group("status")[0].upper(),
                })
        return r
