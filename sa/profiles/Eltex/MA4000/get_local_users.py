# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MA4000.get_local_users"
    interface = IGetLocalUsers

    def execute(self):
        r = []
        t = parse_table(self.cli("show users"), footer=r"system users\.")
        for i in t:
            if i[1] == "15":
                user_class = "superuser"
            elif i[1] == "0":
                user_class = "user"
            else:
                user_class = "operator"
            r += [{"username": i[0], "class": user_class, "is_active": True}]
        return r
