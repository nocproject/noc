# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import datetime
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers


class Script(NOCScript):
    name = "Linksys.SPS2xx.get_local_users"
    implements = [IGetLocalUsers]

    rx_name = re.compile(
        r"^username\s+(?P<username>\S+)\s+password .* level (?P<privilege>\d+) encrypted$")

    def execute(self):
        data = self.cli("show running-config")
        r = []
        data = data.split("\n")
        for i in range(len(data)):
            name = self.rx_name.match(data[i].strip())
            if name:
                privilege = name.group("privilege")
                if privilege == "15":
                    user_class = "superuser"
                else:
                    user_class = privilege
                r += [{
                    "username": name.group("username"),
                    "class": user_class,
                    "is_active": True
                    }]
        return r
