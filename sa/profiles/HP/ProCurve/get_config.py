# ---------------------------------------------------------------------
# HP.ProCurve.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "HP.ProCurve.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r", **kwargs):
        assert policy in ("r", "s")
        if self.is_old_cli:
            config = self.cli("show config")
        elif policy == "s":
            config = self.cli("display saved-configuration")
        else:
            config = self.cli("display current-configuration")
        if " command is supported only" in config:
            raise self.NotSupportedError("Required permission")
        # config = self.cli("show config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
