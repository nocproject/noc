# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_params
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdict import IGetDict


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_params"
    interface = IGetDict

    def execute_cli(self):
        config = self.http.get(
            "/snapshots/full/config.json",
            json=True,
        )

        return config
