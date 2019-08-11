# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Beward.BD.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Beward.BD.get_config"
    interface = IGetConfig

    def execute(self, **kwargs):
        config = self.http.get(
            "/cgi-bin/admin/param.cgi?action=list", json=False, cached=True, use_basic=True
        )
        users = self.http.get(
            "/cgi-bin/admin/privacy.cgi?", json=False, cached=True, use_basic=True
        )
        return config + "\n".join("user=" + u for u in users.splitlines() if u.strip())
