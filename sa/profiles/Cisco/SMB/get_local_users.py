# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Cisco.SMB.get_local_users
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Cisco.SMB.get_local_users"
    interface = IGetLocalUsers
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(r"^\s*(?P<username>\S+)\s+(?P<privilege>\d+).*$")

    def execute(self):
        data = self.cli("show user accounts")
        r = []
<<<<<<< HEAD
        for ll in data.split("\n"):
            match = self.rx_line.match(ll.strip())
=======
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip())
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                })
=======
                    })
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
