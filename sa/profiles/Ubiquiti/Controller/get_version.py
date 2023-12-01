# ---------------------------------------------------------------------
# Ubiquiti.Controller.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ubiquiti.Controller.get_version"
    interface = IGetVersion
    cache = True

    def execute(self):
        v = self.http.get("/v2/api/info", json=True)
        # uptime
        return {
            "vendor": "Ubiquiti",
            "platform": v["system"]["standalone"]["platform_type"],
            "version": v["system"]["version"],
        }
