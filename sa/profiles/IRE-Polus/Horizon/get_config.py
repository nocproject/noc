# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import pprint

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_config"
    cache = True
    interface = IGetConfig

    def execute(self, **kwargs):
        config = self.http.get(
            "/snapshots/full/config.json",
            json=True,
        )

        return pprint.pformat(config)
