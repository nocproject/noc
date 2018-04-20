# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# OS.Linux.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "OS.Linux.get_local_users"
    interface = IGetLocalUsers
=======
##----------------------------------------------------------------------
## OS.Linux.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers


class Script(noc.sa.script.Script):
    name = "OS.Linux.get_local_users"
    implements = [IGetLocalUsers]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        data = self.cli("cat /etc/passwd")
        r = []
        data = data.split("\n")
        for s in data:
            u = s.split(':')
            if len(u) > 3:
                name = u[0]
                user_id = int(u[2])
                if user_id == 0:
                    user_class = "superuser"
                elif user_id < 1000:
                    user_class = "system"
                else:
                    user_class = "operator"
                r.append({
                        "username": name,
                        "class": user_class,
                        "is_active": True
                        })
        if not r:
                    raise Exception("Not implemented")
        return r
