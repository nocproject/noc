# -*- coding: utf-8 -*-
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
    rx_line = re.compile(r"^username (?P<username>\S+) password( \d)? \S+\nusername \S+ privilege (?P<privilege>\d+)$", re.MULTILINE)

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
