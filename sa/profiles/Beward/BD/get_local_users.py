# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Beward.BD.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "Beward.BD.get_local_users"
    interface = IGetLocalUsers

    def execute(self):
        r = []
        res = self.http.get("/cgi-bin/admin/privacy.cgi", use_basic=True)
        for line in res.splitlines()[1:]:
            if not line:
                continue
            r += [{"username": line.split(":")[0], "class": "admin"}]  # not API for permission

        return r
