# ---------------------------------------------------------------------
# Ubiquiti.Controller.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Ubiquiti.Controller..get_capabilities"

    def execute_platform_cli(self, caps):
        v = self.http.post(
            "/v2/api/sites/overview/",
            orjson.dumps({}),
            headers={"Content-Type": b"application/json"},
            json=True,
            cached=True,
        )
        if v["data"]:
            caps["WiFi | Controller | Sites"] = len(v["data"])
