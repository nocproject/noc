#!./bin/python
# ---------------------------------------------------------------------
# MRT service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService
from noc.config import config


class MRTService(BaseService):
    name = "mrt"
    use_telemetry = config.mrt.enable_command_logging
    use_mongo = True

    async def on_activate(self) -> None:
        self.sae = self.open_rpc("sae")
