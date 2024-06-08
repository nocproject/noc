# ---------------------------------------------------------------------
# Eltex.WOPLR.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Eltex.WOPLR.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        c = self.cli("show-config")
        return self.cleaned_config(c)
