# ---------------------------------------------------------------------
# BDCOM.IOS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "BDCOM.IOS.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        config = self.cli("show running-config")
        config = self.strip_first_lines(config, 4)
        return self.cleaned_config(config)
