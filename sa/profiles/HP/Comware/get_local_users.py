# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "HP.Comware.get_local_users"
    interface = IGetLocalUsers

    rx_line = re.compile(
        r"The contents of local user (?P<username>\S+):\n"
        r" State:\s+(?P<state>\S+)\n"
        r" ServiceType:.+?\n"
        r" Access-limit:.+?\n"
        r" User-group:\s+\S+\n"
        r" Bind attributes:\n"
        r" Authorization attributes:\n"
        r"  User Privilege:\s+(?P<privilege>\d+)\n",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("display local-user")):
            r += [{
                "username": match.group("username"),
                "class": {
                    "3": "superuser",
                    "2": "operator",
                    "1": "operator"}[match.group("privilege")],
                "is_active": (match.group("state") == "Active")
                }]
        return r
