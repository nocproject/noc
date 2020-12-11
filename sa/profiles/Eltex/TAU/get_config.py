# ---------------------------------------------------------------------
# Eltex.TAU.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.TAU.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        self.cli("config")
        try:
            show = self.cli("show")
            self.cli("exit")
        except self.CLISyntaxError:
            self.cli("exit")
            show = self.cli("show configuration")
        return self.cleaned_config(show)
