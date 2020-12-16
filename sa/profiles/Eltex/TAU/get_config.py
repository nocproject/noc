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
        if self.is_tau4:
            c = self.cli("cat /etc/config/cfg.yaml", cached=True)
        elif self.is_tau8:
            c = self.cli("cat /etc/config/*", cached=True)
        else:
            c = self.cli("cat /tmp/etc/config/cfg.yaml")
        return self.cleaned_config(c)
