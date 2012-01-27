# -*- coding: utf-8 -*-
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
import re
import datetime


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_local_users"
    implements = [IGetLocalUsers]
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
