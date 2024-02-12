# ---------------------------------------------------------------------
# Aruba.ArubaOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.Aruba.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r"):
        assert policy in ("r", "s")
        if policy == "s":
            config = self.cli("show startup-config")
        else:
            config = self.cli("show running-config")
        if config.startswith("Building "):
            # Strip "Building configuration\n\n"
            config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)