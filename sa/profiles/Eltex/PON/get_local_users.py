# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Eltex.PON.get_local_users"
    interface = IGetLocalUsers

    rx_name = re.compile(
        r"^(?P<username>\S+)\s+\((?P<privilege>\S+)\)$")

    def execute(self):
        data = self.cli("user list")
        r = []
        data = data.split("\n")
        for i in range(len(data)):
            name = self.rx_name.search(data[i].strip())
            if name:
                if name.group("privilege"):
                    privilege = name.group("privilege")
                    # privileged operator nonprivileged
                if privilege == "privileged":
                    user_class = "superuser"
                else:
                    user_class = privilege
                r.append({
                    "username": name.group("username"),
                    "class": user_class,
                    "is_active": True
                    })
        return r
