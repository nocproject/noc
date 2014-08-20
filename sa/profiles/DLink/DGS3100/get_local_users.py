# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_local_users
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLocalUsers
import re


class Script(noc.sa.script.Script):
    name = "DLink.DGS3100.get_local_users"
    implements = [IGetLocalUsers]
    rx_line = re.compile(
        r"^\s*(?P<username>\S+)\s+"
        r"(?P<privilege>Admin|Operator|User|Power_User)\s*$",
        re.MULTILINE
    )

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show account")):
            r += [{
                "username": match.group("username"),
                "class": {
                    "Admin": "superuser",
                    "Operator": "operator",
                    "User": "operator",
                    "Power_User": "operator"
                }[match.group("privilege")],
                "is_active": True
            }]
        return r
