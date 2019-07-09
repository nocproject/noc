# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.get_local_users"
    interface = IGetLocalUsers
    rx_line = re.compile(r"^(?P<username>\S+)\s+(?P<privilege>1|15)$")

    def execute(self):
        data = self.cli("show users accounts")
        r = []
        for l in data.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r += [
                    {
                        "username": match.group("username"),
                        "class": {"15": "superuser", "1": "operator"}[match.group("privilege")],
                        "is_active": True,
                    }
                ]
        return r
