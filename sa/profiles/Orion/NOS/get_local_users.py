# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Orion.NOS.get_local_users"
    interface = IGetLocalUsers

    rx_line = re.compile(
        r"^\s*(?P<username>\S+)\s+(?P<privilege>\d+)\s+Local\s*$",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show user")):
            if match.group("privilege") == "15":
                u_class = "superuser"
            else:
                u_class = "operator"
            r += [{
                "username": match.group("username"),
                "class": u_class,
                "is_active": True
            }]
        return r
