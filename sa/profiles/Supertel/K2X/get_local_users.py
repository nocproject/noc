# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers


class Script(NOCScript):
    name = "Supertel.K2X.get_local_users"
    implements = [IGetLocalUsers]

    rx_users = re.compile(
        r"(?P<name>\S+)\s+(?P<privilege>\d+)",
        re.MULTILINE)

    def execute(self):
        cmd = "show users accounts"
        r = []
        for match in self.rx_users.finditer(self.cli(cmd)):
            user = match.group("name")
            privilege = match.group("privilege")
            user_class = "operator"
            if privilege == "15":
                user_class = "superuser"
            r.append({
                "username": user,
                "class": user_class,
                "is_active": True
                })
        return r
