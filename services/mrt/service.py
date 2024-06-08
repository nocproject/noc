#!./bin/python
# ---------------------------------------------------------------------
# MRT service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class MRTService(FastAPIService):
    name = "mrt"
    use_telemetry = config.mrt.enable_command_logging
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/mrt`)"

    async def on_activate(self):
        self.sae = self.open_rpc("sae")


if __name__ == "__main__":
    MRTService().start()
