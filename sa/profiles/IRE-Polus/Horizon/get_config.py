# ---------------------------------------------------------------------
# IRE-Polus.Horizon.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "IRE-Polus.Horizon.get_config"
    cache = True
    interface = IGetConfig

    def execute(self, **kwargs):
        v = self.cli("show config")
        return v
