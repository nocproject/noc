# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "HP.1910.get_local_users"
    interface = IGetLocalUsers

    rx_name = re.compile(
        r"^The contents of local user\s+(?P<username>\S+):$")
    rx_status = re.compile(r"^\s+State:\s+(?P<status>\S+)\s*$")
    rx_priv = re.compile(r"^\s+User Privilege:\s+(?P<privilege>\d+)$")

    def execute(self):
        data = self.cli("display local-user")
        r = []
        data = data.split("\n")
        for i in range(len(data)):
            name = self.rx_name.search(data[i])
            if name:
                i = i + 1
                stat = self.rx_status.search(data[i])
                status = stat.group("status") == 'Active'
                i = i + 6
                priv = self.rx_priv.search(data[i])
                privilege = priv.group("privilege")
                if privilege == "3":
                    user_class = "superuser"
                else:
                    user_class = privilege
                r.append({
                    "username": name.group("username"),
                    "class": user_class,
                    "is_active": True
                    })
        return r
