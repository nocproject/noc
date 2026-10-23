# ---------------------------------------------------------------------
# BDCOM.xPON.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "BDCOM.xPON.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r"):
        assert policy in ("r", "s")
        if policy == "s":
            config = self.cli("show configuration")
        else:
            config = self.cli("show running-config")
        return self.cleaned_config(config)
