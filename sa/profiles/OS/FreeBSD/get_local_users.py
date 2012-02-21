# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers


class Script(NOCScript):
    name = "OS.FreeBSD.get_local_users"
    implements = [IGetLocalUsers]

    def execute(self):
        data = self.cli("cat /etc/passwd")
        r = []
        data = data.split("\n")
        for s in data:
            if s.startswith("#"):
                continue
            u = s.split(':')
            if len(u) > 3:
                name = u[0]
                user_id = int(u[2])
                user_gid = int(u[3])
                if user_id == 0:
                    user_class = "superuser"
                elif user_id > 1000 and user_id < 65534:
                    if user_gid == 0:
                        user_class = "operator"
                    else:
                        user_class = "user"
                else:
                    continue
                r.append({
                    "username": name,
                    "class": user_class,
                    "is_active": True
                })
        if not r:
            raise Exception("Not implemented")
        return r
