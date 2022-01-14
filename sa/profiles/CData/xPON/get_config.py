# ---------------------------------------------------------------------
# CData.xPON.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "CData.xPON.get_config"
    interface = IGetConfig

    def execute_cli(self, **kwargs):
        try:
            config = self.cli("show current-config")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return self.cleaned_config(config)
