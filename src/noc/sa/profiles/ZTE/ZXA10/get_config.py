# ---------------------------------------------------------------------
# ZTE.ZXA10.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "ZTE.ZXA10.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = self.cli("show running-config")
        if "!<mim>" in config:  # Found in C620/C650
            config = self.strip_first_lines(config, 5)
        else:
            config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
