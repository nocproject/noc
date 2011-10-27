# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re,datetime
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers

rx_name = re.compile(r"^username\s+(?P<username>\S+)\s+password encrypted.*")
rx_priv = re.compile(r"^(\S+\s|\s+\S+\s|\S+\s+\S+\s)+(?P<privilege>\d+)")

class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_local_users"
    implements = [IGetLocalUsers]
    def execute(self):
        data = self.cli("show running-config")
        r = []
        data = data.split("\n")
        for i in range(len(data)):
            name = rx_name.match(data[i].strip())
            if name:
                user_class = "operator"
                i = i + 1
                priv = rx_priv.match(data[i].strip())
                privilege = priv.group("privilege")
                if privilege:
                    if privilege == "15":
                        user_class = "superuser"
                    else:
                        user_class = privilege
                r.append({
                    "username" : name.group("username"),
                    "class"    : user_class,
                    "is_active": True
                    })
        return r
