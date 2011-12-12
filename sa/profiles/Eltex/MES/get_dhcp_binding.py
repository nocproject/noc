# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetDHCPBinding


class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_dhcp_binding"
    implements = [IGetDHCPBinding]

    rx_line = re.compile(
        r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+(?P<expire>.+?)\s+(?P<type>Automatic|Manual)$",
        re.IGNORECASE)

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
