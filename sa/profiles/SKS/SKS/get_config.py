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

        config, e1_error = None, False
        if policy == "r":
            try:
                config = self.cli("show running-config")
            except self.CLIOperationError:
                e1_error = True
        if policy == "s" or not config:
            try:
                config = self.cli("show startup-config")
            except self.CLISyntaxError:
                config = self.cli("show configuration")
        r = [{"name": "main", "config": self.cleaned_config(config)}]
        if e1_error:
            r += [
                {
                    "name": "error",
                    "config": "%LCLI-W-E1MESSAGE: E1 units are not yet updated, cannot show running config",
                }
            ]

        return r
