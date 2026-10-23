# ---------------------------------------------------------------------
# Ubiquiti.Controller.get_uptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetuptime import IGetUptime


class Script(BaseScript):
    name = "Ubiquiti.Controller.get_uptime"
    interface = IGetUptime
    cache = True

    def execute(self):
        v = self.http.get("/v2/api/info", json=True)
        # uptime
        return float(v["system"]["uptime"])
