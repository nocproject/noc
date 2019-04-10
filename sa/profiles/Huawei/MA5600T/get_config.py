# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Huawei.MA5600T.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r", **kwargs):
        assert policy in ("r", "s")
        try:
            if policy == "s":
                config = self.cli("display saved-configuration")
            else:
                config = self.cli("display current-configuration")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return self.cleaned_config(config)
