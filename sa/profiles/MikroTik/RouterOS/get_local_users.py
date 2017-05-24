# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_local_users
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlocalusers import IGetLocalUsers


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_local_users"
    interface = IGetLocalUsers

    def execute(self):
        return [{
            "username": r["name"],
            "class": r["group"],
            "is_active": not ("X" in f)
        } for n, f, r in self.cli_detail(
            "/user print detail without-paging")]
