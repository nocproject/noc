# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.ISW.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Extreme.ISW.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r"):
        assert policy in ("r", "s")
        if policy == "s":
            config = self.cli("show startup-config")
        else:
            config = self.cli("flash:startup-config")
        return self.cleaned_config(config)
