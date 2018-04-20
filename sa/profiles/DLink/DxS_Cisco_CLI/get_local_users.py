# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_local_users"
    interface = IGetLocalUsers
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLocalUsers
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_local_users"
    implements = [IGetLocalUsers]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^username (?P<username>\S+) password( \d)? \S+\nusername \S+ "
        r"privilege (?P<privilege>\d+)$", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show run | i username")):
            privilege = match.group("privilege")
            if privilege == "15":
                user_class = "superuser"
            else:
                user_class = "operator"
            r += [{
                "username": match.group("username"),
                "class": user_class,
                "is_active": True
                }]
        return r
