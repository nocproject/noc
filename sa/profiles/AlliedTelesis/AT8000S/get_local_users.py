# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re
import datetime


<<<<<<< HEAD
class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.get_local_users"
    interface = IGetLocalUsers
=======
class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_local_users"
    implements = [IGetLocalUsers]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(r"^(?P<username>\S+)\s+(?P<privilege>1|15)$")

    def execute(self):
        data = self.cli("show users accounts")
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r.append({
                    "username": match.group("username"),
                    "class": {"15": "superuser",
                        "1": "operator"}[match.group("privilege")],
                    "is_active": True
                    })
        return r
