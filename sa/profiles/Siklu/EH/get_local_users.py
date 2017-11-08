# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Siklu.EH.get_local_users"
    interface = IGetLocalUsers

    rx_line = re.compile(
        r"^\s*(?P<username>\S+)\s+(?P<privilege>\S+)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("show user")):
            username = match.group("username")
            privilege = match.group("privilege")
            if (username == "name") and (privilege == "type"):
                continue
            if privilege == "admin":
                privilege = "superuser"
            else:
                privilege = "operator"
            r += [{"username": username, "class": privilege}]
        return r
