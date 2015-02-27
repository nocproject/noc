# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers


class Script(NOCScript):
    name = "Cisco.SMB.get_local_users"
    implements = [IGetLocalUsers]
    rx_line = re.compile(r"^\s*(?P<username>\S+)\s+(?P<privilege>\d+).*$")

    def execute(self):
        data = self.cli("show user accounts")
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                user_class = "operator"
                privilege = match.group("privilege")
                if privilege:
                    if privilege == "15":
                        user_class = "superuser"
                    else:
                        user_class = privilege
                r.append({
                    "username": match.group("username"),
                    "class": user_class,
                    "is_active": True
                    })
        return r
