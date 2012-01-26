# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers
import re
import datetime


class Script(noc.sa.script.Script):
    name = "Cisco.IOS.get_local_users"
    implements = [IGetLocalUsers]
    rx_line = re.compile(r"^username\s+(?P<username>\S+)(?:\s+.*privilege\s+(?P<privilege>\d+))?.*$")

    def execute(self):
        data = self.cli("show running-config | include ^username")
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
