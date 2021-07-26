# ---------------------------------------------------------------------
# SKS.SKS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "SKS.SKS.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r"):
        assert policy in ("r", "s")
        if policy == "s":
            try:
                config = self.cli("show startup-config")
            except self.CLISyntaxError:
                config = self.cli("show configuration")
        else:
            config = self.cli("show running-config")
        try:
            i = config.index("e1 unit-1")
        except ValueError:
            try:
                i = config.index("!")
                config = config[i:]
            except ValueError:
                pass
        return self.cleaned_config(config)
