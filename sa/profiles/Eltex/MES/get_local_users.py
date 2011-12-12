# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers


class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_local_users"
    implements = [IGetLocalUsers]

    rx_name = re.compile(
        r"^username\s+(?P<username>\S+)\s+password encrypted (\S+\s+privilege\s+(?P<privilege>\d+)|.*)")
    rx_priv = re.compile(r"^(\S+\s|\s+\S+\s|\S+\s+\S+\s)+(?P<privilege>\d+)")

    def execute(self):
        data = self.cli("show running-config")
        r = []
        data = data.split("\n")
        for i in range(len(data)):
            name = self.rx_name.search(data[i].strip())
            if name:
                user_class = "operator"
                if name.group("privilege"):
                    privilege = name.group("privilege")
                else:
                    i = i + 1
                    priv = self.rx_priv.match(data[i].strip())
                    privilege = priv.group("privilege")
                if privilege == "15":
                    user_class = "superuser"
                else:
                    user_class = privilege
                r.append({
                    "username": name.group("username"),
                    "class": user_class,
                    "is_active": True
                    })
        return r
