# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers
=======
##----------------------------------------------------------------------
## DLink.DxS.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re
import datetime


<<<<<<< HEAD
class Script(BaseScript):
    name = "DLink.DxS.get_local_users"
    interface = IGetLocalUsers
=======
class Script(noc.sa.script.Script):
    name = "DLink.DxS.get_local_users"
    implements = [IGetLocalUsers]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(r"^\s*(?P<username>\S+)\s+(?P<privilege>Admin|Operator|User|Power_User)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show account")):
            r += [{
                "username": match.group("username"),
                "class": {
                    "Admin": "superuser",
                    "Operator": "operator",
                    "User": "operator",
                    "Power_User": "operator"}[match.group("privilege")],
                "is_active": True
                }]
        return r
